from fastapi import APIRouter, Query, Depends
from app.services.product_service import search_products, compare_products, get_product
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import asyncio

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/search")
async def search_products_endpoint(
    query: str = Query(...),
    store: str | None = None,
    categoria: str | None = Query(None, description="construccion|soldadura|pintura|plomeria"),
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    result = await search_products(db, query, store, min_price, max_price, page, limit)
    # Homecenter único scraper — multicategoría: busca en TODAS las categorías (construcción, soldadura, pintura, plomería, herramientas)
    # Eliminamos filtro por categoría: siempre busca en todas para que "tubo pvc" encuentre aunque esté en plomería
    if not result["products"] or True:  # siempre complementar con scraping multicategoría
        from app.scrapers.homecenter import HomecenterScraper
        scraper = HomecenterScraper()
        mocked = await scraper.search_all_categories(query)
        if not mocked:
            mocked = await scraper.search(query)
        if min_price is not None:
            mocked = [m for m in mocked if m["precio"] >= min_price]
        if max_price is not None:
            mocked = [m for m in mocked if m["precio"] <= max_price]
        # si DB tenía resultados, mezclarlos con los scrapeados (prioriza scrapeados que tienen precio real)
        if mocked:
            return {"products": mocked[:24], "total": len(mocked), "page": 1}
    if result["products"]:
        return result
    return {"products": [], "total": 0, "page": 1}


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
