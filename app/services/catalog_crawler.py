"""Crawl nocturno del catálogo de Homecenter.

Recorre las categorías mapeadas de forma paginada, guarda cada producto en
toolsprice_catalog_products con upsert por sku y registra la corrida en
toolsprice_scraping_logs. Pensado para correr a las 00:00 vía
app.core.catalog_scheduler o manual por POST /api/catalog/crawl.
"""
import asyncio
import json
import math
import re

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.scrapers.homecenter import (
    HomecenterScraper,
    ALL_CATEGORIES,
    CATEGORY_MAP,
)

# Categorías/subcategorías a crawlear (urls únicas + label humano)
def _build_crawl_sources() -> list[tuple[str, str]]:
    labels = HomecenterScraper.CATEGORY_LABELS
    sources: dict[str, str] = {}
    for url in ALL_CATEGORIES:
        sources[url] = labels.get(url, "General")
    for url in CATEGORY_MAP.values():
        if url not in sources:
            sources[url] = labels.get(url, "General")
    return [(url, label) for url, label in sources.items()]


# Parámetros de paginación SSR del sitio: homecenter usa currentpage=N
# (verificado: ?currentpage=2 cambia de página; pagN/page/Nao no afectan el SSR)
_PAGINATION_PARAMS = ("currentpage", "page")

DEFAULT_MAX_PAGES = 300          # tope de seguridad por categoría
_CHUNK = 250                     # tamaño de lote para upsert
_PAGE_DELAY_S = 0.6              # cortesía con robots del sitio
_FETCH_TIMEOUT_S = 25


async def _upsert_products(session, rows: list[dict]) -> int:
    """Upsert por sku con ON CONFLICT DO UPDATE. Devuelve filas procesadas."""
    from app.db.models.models import CatalogProduct

    saved = 0
    for i in range(0, len(rows), _CHUNK):
        chunk = rows[i : i + _CHUNK]
        stmt = pg_insert(CatalogProduct).values(chunk)
        stmt = stmt.on_conflict_do_update(
            index_elements=["sku"],
            set_={
                "nombre": stmt.excluded.nombre,
                "marca": stmt.excluded.marca,
                "categoria": stmt.excluded.categoria,
                "categoria_url": stmt.excluded.categoria_url,
                "precio": stmt.excluded.precio,
                "moneda": stmt.excluded.moneda,
                "unidad_medida": stmt.excluded.unidad_medida,
                "imagen_url": stmt.excluded.imagen_url,
                "url_producto": stmt.excluded.url_producto,
                "disponibilidad": stmt.excluded.disponibilidad,
                "caracteristicas": stmt.excluded.caracteristicas,
                "last_scraped_at": stmt.excluded.last_scraped_at,
                "fecha_actualizacion": datetime.utcnow(),
            },
        )
        await session.execute(stmt)
        saved += len(chunk)
    return saved


def _to_catalog_row(p: dict, categoria: str, categoria_url: str) -> dict | None:
    """Normaliza el producto del scraper a fila para upsert. Requiere sku."""
    sku = str(p.get("caracteristicas", {}).get("sku") or "").strip()
    if not sku:
        return None
    caracteristicas = p.get("caracteristicas") or {}
    return {
        "sku": sku,
        "nombre": (p.get("nombre") or "")[:500],
        "marca": (p.get("marca") or "") or None,
        "categoria": categoria,
        "categoria_url": categoria_url,
        "precio": float(p.get("precio") or 0),
        "moneda": p.get("moneda") or "COP",
        "unidad_medida": p.get("unidad_medida") or "unidad",
        "imagen_url": (p.get("imagen_url") or "") or None,
        "url_producto": p.get("url_producto") or "",
        "disponibilidad": bool(p.get("disponibilidad", True)),
        "caracteristicas": json.dumps(caracteristicas, ensure_ascii=False),
        "last_scraped_at": datetime.utcnow(),
    }


def _total_pages(html: str) -> int | None:
    """Extrae pagination.count/perPage del __NEXT_DATA__ y calcula nº de páginas."""
    m = re.search(
        r'"pagination"\s*:\s*\{[^{}]*"count"\s*:\s*(\d+)\s*,\s*"perPage"\s*:\s*(\d+)',
        html,
    )
    if m:
        count, per_page = int(m.group(1)), int(m.group(2))
        if per_page > 0 and count > 0:
            return math.ceil(count / per_page)
    return None


async def _crawl_category(
    scraper: HomecenterScraper,
    url: str,
    label: str,
    max_pages: int,
    seen_skus: set[str],
    rows: dict[str, dict],
) -> int:
    """Crawlea una categoría paginando (currentpage=N). Devuelve nº de páginas crawleadas."""
    page_param = _PAGINATION_PARAMS[0]
    pages_ok = 0
    total_pages = None
    for page in range(1, max_pages + 1):
        if total_pages is not None and page > total_pages:
            break
        page_url = url if page == 1 else f"{url}?{page_param}={page}"
        try:
            html = await scraper._fetch(page_url, timeout=_FETCH_TIMEOUT_S)
        except Exception as e:
            print(f"[catalog_crawl] fetch fail {page_url}: {e}")
            continue
        await asyncio.sleep(_PAGE_DELAY_S)
        if total_pages is None:
            tp = _total_pages(html)
            if tp:
                total_pages = min(tp, max_pages)
        products = scraper._parse_ldjson_search(html, categoria_hint=label, limit=500)
        if not products:
            if page == 1:
                break
            # probar parámetro de paginación alternativo antes de rendirse
            if page_param != _PAGINATION_PARAMS[-1]:
                page_param = _PAGINATION_PARAMS[-1]
                continue
            break

        new_items = 0
        for p in products:
            row = _to_catalog_row(p, label, url)
            if not row:
                continue
            sku = row["sku"]
            if sku not in seen_skus:
                seen_skus.add(sku)
                rows[sku] = row
                new_items += 1
        pages_ok += 1
        # última página: la respuesta trae menos productos de lo normal
        if len(products) < 20:
            break
        if new_items == 0:
            break
    return pages_ok


async def run_catalog_crawl(max_pages: int = DEFAULT_MAX_PAGES) -> dict:
    """Corrida completa: crawl de todas las categorías + upsert + log.

    Nunca lanza excepción hacia afuera: todo queda en el ScrapingLog.
    """
    from app.db.session import async_session_factory
    from app.db.models.models import CatalogProduct, ScrapingLog

    started = datetime.utcnow()
    scraper = HomecenterScraper()
    seen_skus: set[str] = set()
    rows: dict[str, dict] = {}
    pages_stats: dict[str, int] = {}

    try:
        for url, label in _build_crawl_sources():
            try:
                n = await _crawl_category(scraper, url, label, max_pages, seen_skus, rows)
                pages_stats[label] = n
                print(f"[catalog_crawl] {label}: {n} páginas, {len(rows)} skus acumulados")
            except Exception as e:
                print(f"[catalog_crawl] categoría {label} falló: {e}")

        # upsert de todos los productos acumulados
        rows_list = list(rows.values())
        async with async_session_factory() as session:
            saved = await _upsert_products(session, rows_list)
            # marcar como sin stock los productos que ya no aparecen en el sitio
            stale = await session.execute(
                select(CatalogProduct.sku).where(CatalogProduct.last_scraped_at < started)
            )
            stale_skus = [r[0] for r in stale.all()]
            for j in range(0, len(stale_skus), _CHUNK):
                chunk = stale_skus[j : j + _CHUNK]
                await session.execute(
                    CatalogProduct.__table__.update()
                    .where(CatalogProduct.sku.in_(chunk))
                    .values(disponibilidad=False, fecha_actualizacion=datetime.utcnow())
                )
            await session.commit()

        finished = datetime.utcnow()
        summary = {
            "status": "success",
            "started": started.isoformat(),
            "finished": finished.isoformat(),
            "products": len(rows_list),
            "categories": pages_stats,
        }
        async with async_session_factory() as log_session:
            log_session.add(ScrapingLog(
                tienda="Homecenter",
                action="catalog_crawl",
                status="success",
                error_message=json.dumps(summary, ensure_ascii=False)[:500],
                duration_ms=int((finished - started).total_seconds() * 1000),
            ))
            await log_session.commit()
        return summary
    except Exception as e:
        async with async_session_factory() as log_session:
            log_session.add(ScrapingLog(
                tienda="Homecenter",
                action="catalog_crawl",
                status="error",
                error_message=str(e)[:500],
                duration_ms=int((datetime.utcnow() - started).total_seconds() * 1000),
            ))
            await log_session.commit()
        return {"status": "error", "error": str(e)}


async def get_crawl_stats() -> dict:
    """Estado del catálogo: total, frescos (últimas 24h) y últimos crawls."""
    from app.db.session import async_session_factory
    from app.db.models.models import CatalogProduct, ScrapingLog
    from sqlalchemy import func

    async with async_session_factory() as session:
        total = (await session.execute(select(func.count()).select_from(CatalogProduct))).scalar() or 0
        fresh = (await session.execute(
            select(func.count()).select_from(CatalogProduct)
            .where(CatalogProduct.last_scraped_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0))
        )).scalar() or 0
        available = (await session.execute(
            select(func.count()).select_from(CatalogProduct).where(CatalogProduct.disponibilidad == True)  # noqa: E712
        )).scalar() or 0
    logs = []
    try:
        async with async_session_factory() as session:
            res = await session.execute(
                select(ScrapingLog)
                .where(ScrapingLog.action == "catalog_crawl")
                .order_by(ScrapingLog.created_at.desc())
                .limit(10)
            )
            for log in res.scalars():
                logs.append({
                    "status": log.status,
                    "created_at": log.created_at.isoformat(),
                    "duration_ms": log.duration_ms,
                    "detail": log.error_message,
                })
    except Exception:
        pass
    return {"total": total, "todays": fresh, "available": available, "logs": logs}
