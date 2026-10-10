from app.services.budget_service import create_budget, get_budgets, get_budget, delete_budget, update_budget, duplicate_budget
from app.services.pdf_export import generate_budget_pdf
from app.db.session import get_db
from app.core.security import verify_token
from fastapi import APIRouter, Depends, HTTPException, Response, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.budget import BudgetCreate, BudgetResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(prefix="/budgets", tags=["budgets"])

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    # Soporta Authorization: Bearer <token> y credentials de HTTPBearer
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    else:
        auth = request.headers.get("Authorization") or request.headers.get("authorization")
        if auth and auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated - falta token")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload


@router.post("/", response_model=BudgetResponse)
async def create_budget_endpoint(
    budget: BudgetCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Validar que el usuario aún existe (token viejo tras down -v puede tener user_id huérfano)
    from app.db.models.models import User
    from sqlalchemy import select
    from sqlalchemy.exc import IntegrityError
    try:
        u = await db.execute(select(User).filter(User.id == user["sub"]))
        if not u.scalars().first():
            raise HTTPException(status_code=401, detail="Sesión expirada (usuario no existe). Por favor inicia sesión nuevamente.")
        result = await create_budget(db, user["sub"], budget.items, budget.tax_rate, budget.budget_type, budget.name)
    except HTTPException:
        raise
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=401, detail="Sesión inválida - token con usuario inexistente. Inicia sesión nuevamente.")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear presupuesto: {str(e)[:200]}")
    return BudgetResponse(
        id=result.id,
        name=result.name,
        description=result.description,
        budget_type=result.budget_type,
        subtotal=result.subtotal,
        tax_amount=result.tax_amount,
        total=result.total,
        status=result.status,
        created_at=result.created_at.isoformat()
    )


@router.get("/", response_model=list[BudgetResponse])
async def list_budgets(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    budgets = await get_budgets(db, user["sub"])
    # mapear con fallback para presupuestos antiguos sin budget_type
    return [
        BudgetResponse(
            id=b.id,
            name=b.name,
            description=b.description,
            budget_type=getattr(b, "budget_type", None) or "construccion",
            subtotal=b.subtotal,
            tax_amount=b.tax_amount,
            total=b.total,
            status=b.status,
            created_at=b.created_at.isoformat()
        ) for b in budgets
    ]


@router.get("/{budget_id}")
async def get_budget_endpoint(
    budget_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    budget = await get_budget(db, budget_id)
    if not budget or budget.user_id != user["sub"]:
        raise HTTPException(status_code=404, detail="Budget not found")
    # incluir items en la respuesta
    items = budget.__dict__.get("items", [])
    return {
        "id": budget.id,
        "name": budget.name,
        "description": budget.description,
        "budget_type": budget.budget_type,
        "subtotal": budget.subtotal,
        "tax_amount": budget.tax_amount,
        "total": budget.total,
        "status": budget.status,
        "created_at": budget.created_at.isoformat(),
        "items": [{"product_name": i.product_name, "quantity": i.quantity, "unit_price": i.unit_price, "total_price": i.total_price, "product_id": i.product_id} for i in items],
    }


@router.put("/{budget_id}")
async def update_budget_endpoint(
    budget_id: str,
    payload: BudgetCreate,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated = await update_budget(db, budget_id, user["sub"], payload.items, payload.budget_type, payload.name, payload.tax_rate)
    if not updated:
        raise HTTPException(status_code=404, detail="Budget not found")
    items = updated.__dict__.get("items", [])
    return {
        "id": updated.id,
        "name": updated.name,
        "description": updated.description,
        "budget_type": updated.budget_type,
        "subtotal": updated.subtotal,
        "tax_amount": updated.tax_amount,
        "total": updated.total,
        "status": updated.status,
        "created_at": updated.created_at.isoformat(),
        "items": [{"product_name": i.product_name, "quantity": i.quantity, "unit_price": i.unit_price, "total_price": i.total_price} for i in items],
    }


@router.post("/{budget_id}/duplicate")
async def duplicate_budget_endpoint(
    budget_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    dup = await duplicate_budget(db, budget_id, user["sub"])
    if not dup:
        raise HTTPException(status_code=404, detail="Budget not found")
    return BudgetResponse(
        id=dup.id,
        name=dup.name,
        description=dup.description,
        budget_type=dup.budget_type,
        subtotal=dup.subtotal,
        tax_amount=dup.tax_amount,
        total=dup.total,
        status=dup.status,
        created_at=dup.created_at.isoformat()
    )


@router.delete("/{budget_id}")
async def delete_budget_endpoint(
    budget_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # verificar ownership
    b = await get_budget(db, budget_id)
    if not b or b.user_id != user["sub"]:
        raise HTTPException(status_code=404, detail="Budget not found")
    success = await delete_budget(db, budget_id)
    if not success:
        raise HTTPException(status_code=404, detail="Budget not found")
    return {"message": "Budget deleted"}


@router.get("/{budget_id}/export/pdf")
@router.post("/{budget_id}/export/pdf")
async def export_pdf(
    budget_id: str,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    budget = await get_budget(db, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    items = budget.__dict__.get("items", [])

    # Nombre del usuario para la firma del PDF
    preparador_name = None
    try:
        from app.db.models.models import User
        r = await db.execute(select(User).filter(User.id == budget.user_id))
        owner = r.scalars().first()
        if owner and getattr(owner, "name", None):
            preparador_name = owner.name
    except Exception:
        preparador_name = None

    pdf_bytes = generate_budget_pdf(budget, items, preparador_name=preparador_name)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=presupuesto_{budget_id}.pdf"}
    )
