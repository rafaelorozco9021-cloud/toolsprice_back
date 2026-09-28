from fastapi import APIRouter, Query
from app.schemas.labor import LaborSearchResponse
from app.services.labor_service import LABOR_CATALOG, search_labor, list_categorias

router = APIRouter(prefix="/labor", tags=["labor"])

@router.get("/categorias")
def categorias():
    return {"categorias": list_categorias()}

@router.get("/search")
def search(
    query: str = Query("", description="ej: friso, piso ceramica, pintura"),
    categoria: str | None = Query(None, description="Friso|Piso cerámica|Pintura|Plomería|Eléctrico|Soldadura|... o todas"),
    limit: int = 20
):
    tasks = search_labor(query, categoria)
    return {"tasks": tasks[:limit], "total": len(tasks), "categoria": categoria}

@router.get("/catalog")
def catalog():
    return {"tasks": LABOR_CATALOG, "total": len(LABOR_CATALOG)}
