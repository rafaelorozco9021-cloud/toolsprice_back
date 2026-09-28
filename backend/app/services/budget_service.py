from datetime import datetime
from app.db.models.models import Budget, BudgetItem
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


async def create_budget(db: AsyncSession, user_id: str, items: list, tax_rate: float = 0.16, budget_type: str = "construccion", name: str | None = None):
    def _get(item, key, default=None):
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    subtotal = sum(float(_get(item, "unit_price", 0)) * int(_get(item, "quantity", 1)) for item in items)
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    budget = Budget(
        user_id=user_id,
        name=name or f"Presupuesto {datetime.utcnow().strftime('%Y-%m-%d')}",
        description=f"Presupuesto de {budget_type}",
        budget_type=budget_type,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=total,
        status="draft"
    )
    db.add(budget)
    await db.commit()
    await db.refresh(budget)

    for item in items:
        budget_item = BudgetItem(
            budget_id=budget.id,
            product_id=_get(item, "product_id"),
            product_name=_get(item, "product_name", ""),
            quantity=int(_get(item, "quantity", 1)),
            unit_price=float(_get(item, "unit_price", 0)),
            total_price=float(_get(item, "unit_price", 0)) * int(_get(item, "quantity", 1))
        )
        db.add(budget_item)

    await db.commit()
    return budget


async def get_budgets(db: AsyncSession, user_id: str):
    result = await db.execute(select(Budget).filter(Budget.user_id == user_id).order_by(Budget.created_at.desc()))
    return list(result.scalars().all())


async def get_budget(db: AsyncSession, budget_id: str):
    result = await db.execute(select(Budget).filter(Budget.id == budget_id))
    budget = result.scalars().first()

    if budget:
        items_result = await db.execute(select(BudgetItem).filter(BudgetItem.budget_id == budget_id))
        # bypass SQLAlchemy lazy loader (async no permite lazy load)
        budget.__dict__["items"] = list(items_result.scalars().all())

    return budget


async def update_budget(db: AsyncSession, budget_id: str, user_id: str, items: list, budget_type: str | None = None, name: str | None = None, tax_rate: float = 0.16):
    result = await db.execute(select(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id))
    budget = result.scalars().first()
    if not budget:
        return None

    def _get(item, key, default=None):
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    # recalcular totales
    subtotal = sum(float(_get(it, "unit_price", 0)) * int(_get(it, "quantity", 1)) for it in items)
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    if name:
        budget.name = name
    if budget_type:
        budget.budget_type = budget_type
        budget.description = f"Presupuesto de {budget_type}"
    budget.subtotal = subtotal
    budget.tax_amount = tax_amount
    budget.total = total

    # reemplazar items: borrar anteriores e insertar nuevos
    old = await db.execute(select(BudgetItem).filter(BudgetItem.budget_id == budget_id))
    for oi in old.scalars().all():
        await db.delete(oi)
    await db.flush()

    for it in items:
        bi = BudgetItem(
            budget_id=budget.id,
            product_id=_get(it, "product_id"),
            product_name=_get(it, "product_name", ""),
            quantity=int(_get(it, "quantity", 1)),
            unit_price=float(_get(it, "unit_price", 0)),
            total_price=float(_get(it, "unit_price", 0)) * int(_get(it, "quantity", 1))
        )
        db.add(bi)
    await db.commit()
    await db.refresh(budget)
    items_r = await db.execute(select(BudgetItem).filter(BudgetItem.budget_id == budget.id))
    budget.__dict__["items"] = list(items_r.scalars().all())
    return budget


async def duplicate_budget(db: AsyncSession, budget_id: str, user_id: str):
    orig = await get_budget(db, budget_id)
    if not orig or orig.user_id != user_id:
        return None
    items = orig.__dict__.get("items", [])
    # convertir a dicts para create
    dict_items = [{"product_name": i.product_name, "quantity": i.quantity, "unit_price": i.unit_price, "total_price": i.total_price, "product_id": i.product_id} for i in items]
    return await create_budget(db, user_id, dict_items, tax_rate=0.16, budget_type=orig.budget_type, name=orig.name + " (copia)")


async def delete_budget(db: AsyncSession, budget_id: str):
    from sqlalchemy import delete as sql_delete
    # borrar items primero para evitar FK y evitar lazy load con __dict__
    await db.execute(sql_delete(BudgetItem).where(BudgetItem.budget_id == budget_id))
    result = await db.execute(select(Budget).filter(Budget.id == budget_id))
    budget = result.scalars().first()
    if budget:
        # limpiar posible cache de items inyectado via __dict__
        budget.__dict__.pop("items", None)
        await db.delete(budget)
        await db.commit()
        return True
    return False
