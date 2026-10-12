from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.budgets import get_current_user
from app.db.session import get_db
from app.schemas.ai import AnalizarObraRequest, AnalizarObraResponse
from app.services.ai_service import analizar_obra

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/analizar-obra", response_model=AnalizarObraResponse)
async def analizar_obra_endpoint(
    payload: AnalizarObraRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analiza la descripción de una obra con IA y devuelve materiales con
    precios reales de Homecenter + mano de obra del tabulador."""
    try:
        result = await analizar_obra(payload.descripcion)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[AI] analizar-obra error: {e}")
        raise HTTPException(
            status_code=502,
            detail="No se pudo analizar la obra. Intenta de nuevo en un momento.",
        )
