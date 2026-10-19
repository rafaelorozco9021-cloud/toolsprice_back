"""Búsqueda de productos desde el catálogo pre-scrapeado (toolsprice_catalog_products).

Devuelve el mismo formato que el scraper normalizado para que el frontend
no necesite cambios. Usar pg_trgm (similarity) para el ranking.
"""
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession


def _row_to_dict(p) -> dict:
    return {
        "nombre": p.nombre,
        "categoria": p.categoria or "Homecenter",
        "precio": float(p.precio or 0),
        "moneda": p.moneda or "COP",
        "unidad_medida": p.unidad_medida or "unidad",
        "marca": p.marca or "",
        "caracteristicas": {"sku": p.sku},
        "url_producto": p.url_producto,
        "imagen_url": p.imagen_url or "",
        "tienda": p.fuente or "Homecenter",
        "disponibilidad": bool(p.disponibilidad),
        "fecha_actualizacion": p.fecha_actualizacion.isoformat() if p.fecha_actualizacion else None,
    }


async def search_catalog(
    db: AsyncSession,
    query: str,
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = 1,
    limit: int = 24,
) -> dict:
    from app.db.models.models import CatalogProduct

    q = (query or "").strip()
    if not q:
        return {"products": [], "total": 0, "page": page}

    combined = func.concat_ws(
        " ",
        func.coalesce(CatalogProduct.nombre, ""),
        func.coalesce(CatalogProduct.marca, ""),
        func.coalesce(CatalogProduct.categoria, ""),
    )
    sim = func.similarity(combined, q).label("sim")

    conds = [CatalogProduct.precio > 0]
    conds.append(or_(
        sim > 0.08,
        *[CatalogProduct.nombre.ilike(f"%{t}%") for t in q.lower().split() if t],
    ))
    if min_price is not None:
        conds.append(CatalogProduct.precio >= min_price)
    if max_price is not None:
        conds.append(CatalogProduct.precio <= max_price)

    base = select(CatalogProduct).where(*conds)
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0

    stmt = (
        base.order_by(sim.desc(), CatalogProduct.disponibilidad.desc(), CatalogProduct.precio.asc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    rows = list((await db.execute(stmt)).scalars().all())
    return {"products": [_row_to_dict(p) for p in rows], "total": total, "page": page}
