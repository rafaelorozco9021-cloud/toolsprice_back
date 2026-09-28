from pydantic import BaseModel
from typing import List, Optional

class LaborTask(BaseModel):
    id: str
    nombre: str
    categoria: str
    descripcion: str
    unidad: str
    precio_unitario: float
    moneda: str = "COP"
    rendimiento: str = ""
    incluye_material: bool = False

class LaborSearchResponse(BaseModel):
    tasks: List[LaborTask]
    total: int
    categoria: str | None = None
