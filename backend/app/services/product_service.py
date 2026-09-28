from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from datetime import datetime
from rapidfuzz import process, fuzz


async def search_products(
    db: AsyncSession,
    query: str,
    store: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = 1,
    limit: int = 20
):
    from app.db.models.models import Product

    offset = (page - 1) * limit
    stmt = select(Product)

    if query:
        stmt = stmt.filter(or_(
            Product.nombre.ilike(f"%{query}%"),
            Product.categoria.ilike(f"%{query}%"),
            Product.marca.ilike(f"%{query}%"),
        ))

    if store:
        stmt = stmt.filter(Product.tienda == store)

    if min_price is not None:
        stmt = stmt.filter(Product.precio >= min_price)

    if max_price is not None:
        stmt = stmt.filter(Product.precio <= max_price)

    result = await db.execute(stmt.offset(offset).limit(limit))
    products = list(result.scalars().all())

    total = await db.execute(select(func.count()).select_from(stmt))
    total_count = total.scalar()

    return {"products": products, "total": total_count, "page": page}


async def compare_products(db: AsyncSession, product_ids: list[str]):
    from app.db.models.models import Product

    result = await db.execute(select(Product).filter(Product.id.in_(product_ids)))
    products = list(result.scalars().all())

    return {"products": products, "count": len(products)}


async def get_product(db: AsyncSession, product_id: str):
    from app.db.models.models import Product

    result = await db.execute(select(Product).filter(Product.id == product_id))
    return result.scalars().first()
