from pydantic import BaseModel
from typing import List, Optional


class AnalizarObraRequest(BaseModel):
    descripcion: str


class MaterialSugerido(BaseModel):
    nombre_busqueda: str
    cantidad: float
    unidad: str = "unidad"
    nota: str = ""


class ManoObraSugerida(BaseModel):
    query_tabulador: str
    cantidad: float
    unidad: str = "m²"
    nota: str = ""


class ObraDetectada(BaseModel):
    tipo: str = "General"
    obra_tipo_clave: str = "general"
    descripcion: str = ""
    area_m2: Optional[float] = None
    espesor_m: Optional[float] = None
    medidas_usadas: str = ""
    confianza: str = "media"


class MaterialEnriquecido(BaseModel):
    nombre_busqueda: str
    nombre: str = ""
    cantidad: float = 1
    unidad: str = "unidad"
    nota: str = ""
    # Precio real Homecenter (vacío si no se encontró)
    precio: float = 0
    moneda: str = "COP"
    marca: str = ""
    imagen_url: str = ""
    url_producto: str = ""
    categoria: str = ""
    encontrado: bool = False
    subtotal: float = 0


class ManoObraEnriquecida(BaseModel):
    query_tabulador: str
    nombre: str = ""
    cantidad: float = 1
    unidad: str = "m²"
    nota: str = ""
    precio_unitario: float = 0
    moneda: str = "COP"
    categoria: str = ""
    encontrado: bool = False
    subtotal: float = 0


class AnalizarObraResponse(BaseModel):
    obra: ObraDetectada
    materiales: List[MaterialEnriquecido] = []
    mano_de_obra: List[ManoObraEnriquecida] = []
    subtotal_materiales: float = 0
    subtotal_mano_obra: float = 0
    subtotal: float = 0
    tax_amount: float = 0
    total: float = 0
    advertencias: List[str] = []
