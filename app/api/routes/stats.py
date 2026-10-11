"""Estadísticas públicas para el landing (sin datos personales)."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.db.session import get_db
from app.db.models.models import User, Budget, BudgetItem, SearchLog

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/public")
async def public_stats(db: AsyncSession = Depends(get_db)):
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    total_budgets = (await db.execute(select(func.count()).select_from(Budget))).scalar() or 0

    # Lo más buscado (últimas búsquedas reales)
    top_searches: list[dict] = []
    try:
        rows = (
            await db.execute(
                select(SearchLog.query, func.count().label("c"))
                .group_by(SearchLog.query)
                .order_by(desc("c"))
                .limit(5)
            )
        ).all()
        top_searches = [{"query": q, "count": int(c)} for q, c in rows]
    except Exception:
        top_searches = []

    # Si aún no hay búsquedas registradas, usar lo más cotizado en presupuestos
    if not top_searches:
        try:
            rows = (
                await db.execute(
                    select(BudgetItem.product_name, func.count().label("c"))
                    .group_by(BudgetItem.product_name)
                    .order_by(desc("c"))
                    .limit(5)
                )
            ).all()
            top_searches = [{"query": (n or "")[:40], "count": int(c)} for n, c in rows if n]
        except Exception:
            top_searches = []

    return {
        "total_users": int(total_users),
        "total_budgets": int(total_budgets),
        "top_searches": top_searches,
    }
