from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any, Optional


class ProductSchema(BaseModel):
    nombre: str
    categoria: str
    precio: float
    moneda: str
    unidad_medida: str
    marca: str
    caracteristicas: Dict[str, Any]
    url_producto: str
    imagen_url: str
    tienda: str
    disponibilidad: bool
    fecha_actualizacion: Optional[datetime] = None


class ProductSearchResponse(BaseModel):
    products: list[ProductSchema]
    total: int
    page: int
