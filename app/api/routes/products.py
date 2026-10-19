from fastapi import APIRouter, Query, Depends, Request
from app.services.product_service import search_products, compare_products, get_product
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import asyncio
import re

router = APIRouter(prefix="/products", tags=["products"])


def _norm_query(q: str) -> str:
    q = (q or "").strip().lower()
    q = re.sub(r"\s+", " ", q)
    return q[:120]


async def _log_search(request: Request, query: str):
    """Guarda la búsqueda para 'lo más buscado'. Sesión propia, nunca rompe la búsqueda."""
    try:
        q = _norm_query(query)
        if len(q) < 2:
            return
        user_id = None
        try:
            auth = request.headers.get("Authorization") or ""
            if auth.startswith("Bearer "):
                from app.core.security import verify_token
                payload = verify_token(auth.split(" ", 1)[1])
                if payload:
                    user_id = payload.get("sub")
        except Exception:
            pass
        from app.db.models.models import SearchLog
        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            session.add(SearchLog(query=q, user_id=user_id))
            await session.commit()
    except Exception:
        pass


@router.get("/search")
async def search_products_endpoint(
    request: Request,
    query: str = Query(...),
    store: str | None = None,
    categoria: str | None = Query(None, description="construccion|soldadura|pintura|plomeria"),
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    asyncio.create_task(_log_search(request, query))
    # 1) Búsqueda desde el catálogo pre-scrapeado (rápida, < 200ms)
    try:
        from app.services.catalog_search import search_catalog
        result = await search_catalog(db, query, min_price, max_price, page, limit)
    except Exception as e:
        print(f"[search] catálogo no disponible: {e}")
        result = {"products": [], "total": 0, "page": page}
    if result["products"]:
        return result
    # 2) Fallback: scraping en vivo (catálogo vacío, sin coincidencias o error DB)
    from app.scrapers.homecenter import HomecenterScraper
    scraper = HomecenterScraper()
    mocked = await scraper.search_all_categories(query)
    if not mocked:
        mocked = await scraper.search(query)
    if min_price is not None:
        mocked = [m for m in mocked if m["precio"] >= min_price]
    if max_price is not None:
        mocked = [m for m in mocked if m["precio"] <= max_price]
    return {"products": mocked[:24], "total": len(mocked), "page": 1}


@router.get("/search/live")
async def search_live(
    query: str = Query(...),
    store: str | None = None,
    categoria: str | None = None
) -> Dict[str, Any]:
    from app.scrapers.homecenter import HomecenterScraper

    scraper = HomecenterScraper()
    if categoria:
        products = await scraper.search(query, categoria=categoria)
    else:
        # multicategoría: si no se especifica, buscar en las 4
        products = await scraper.search_all_categories(query)
        if not products:
            products = await scraper.search(query)
    return {"products": products, "total": len(products)}


@router.get("/compare")
async def compare_products_endpoint(
    product_ids: List[str],
    db: AsyncSession = Depends(get_db)
):
    return await compare_products(db, product_ids)


@router.get("/{product_id}")
async def get_product_endpoint(
    product_id: str,
    db: AsyncSession = Depends(get_db)
):
    return await get_product(db, product_id)
