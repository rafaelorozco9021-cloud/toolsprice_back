"""Agente IA que analiza la descripción de una obra y la convierte en
materiales + mano de obra con precios reales.

Proveedor: Google AI Studio (Gemini) vía generateContent.
Flujo: descripción -> modelo (JSON estricto) -> Homecenter (precios reales)
-> tabulador (precios mano de obra) -> presupuesto listo para el carrito.
"""
import asyncio
import json
import re
from typing import Any, Dict, List

import httpx

from app.core.config import settings

SYSTEM_PROMPT = """Eres un maestro de obra colombiano con 20 años de experiencia en construcción,
pintura, plomería, soldadura y remodelación. Analizas la descripción de una obra
y devuelves ÚNICAMENTE un JSON válido, sin texto antes ni después, sin markdown.

Reglas de cálculo (Colombia):
- Mampostería bloque #4 (10x20x40 cm): 14 bloques por m² + 8% de desperdicio.
- Mortero de pega 1:4: 1 bulto de cemento gris x 50 kg rinde ~4 m² de muro.
- Arena lavada: 0.08 m³ por m² de muro.
- Acero/varilla: solo si la obra lo exige (columnas, vigas, zapatas); para un
  muro simple divisorio NO incluyas varilla, indica por qué en "nota".
- Pintura vinilo: 1 galón rinde ~25 m² a 2 manos + 10% desperdicio.
- Piso cerámico: m² + 10% por cortes y desperdicio; pegante 1 bulto x 25 kg
  rinde ~5 m²; fragua (boquilla) 1 kg rinde ~8 m².
- Friso/pañete: 1 bulto de cemento rinde ~3 m² a 1 cm de espesor.
- Redondea cantidades hacia arriba a valores comprables (medios bultos, m³ a 0.25).
- "nombre_busqueda" debe ser corto (1-3 palabras) para buscar en tienda:
  ej "bloque 4", "cemento gris", "arena lavada", "pintura vinilo".
- "query_tabulador" debe coincidir con oficios del tabulador: muro bloque,
  friso, pintura, piso ceramica, enchape, plomeria, electrico, soldadura.
- "cantidad" de mano de obra = área en la unidad del oficio (m², punto, ml).
- NUNCA inventes precios. Solo nombres, cantidades y notas.
- Si la descripción no trae medidas, estima lo mínimo razonable y pon
  "confianza": "baja"; si trae medidas claras, "confianza": "alta".

Formato EXACTO de respuesta (JSON):
{
  "obra": {"tipo": "Mampostería", "descripcion": "...", "area_m2": 7.5,
           "medidas_usadas": "3.00 m de ancho x 2.50 m de alto", "confianza": "alta"},
  "materiales": [
    {"nombre_busqueda": "bloque 4", "cantidad": 114, "unidad": "unidad",
     "nota": "14 bloques/m² + 8% desperdicio"}
  ],
  "mano_de_obra": [
    {"query_tabulador": "muro bloque", "cantidad": 7.5, "unidad": "m²",
     "nota": "Muro bloque #4 pegado"}
  ]
}"""

DEFAULT_MODEL = "gemini-3-flash-preview"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _model_id() -> str:
    # Acepta "gemini-3-flash-preview" o "gemini/gemini-3-flash-preview"
    model = (settings.ai_model or DEFAULT_MODEL).strip()
    if "/" in model:
        model = model.split("/")[-1]
    return model or DEFAULT_MODEL


def _extract_json(text: str) -> Dict[str, Any]:
    """Extrae el primer objeto JSON de la respuesta, aunque venga con texto extra."""
    text = (text or "").strip()
    # Quitar bloques markdown si los trae
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("La IA no devolvió un JSON válido")
    return json.loads(text[start:end + 1])


async def _call_model(descripcion: str) -> Dict[str, Any]:
    api_key = (settings.ai_api_key or "").strip()
    if not api_key:
        raise ValueError("AI_API_KEY no configurada en el servidor")
    model = _model_id()
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": descripcion.strip()[:2000]}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1500,
            "responseMimeType": "application/json",
        },
    }
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(45.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(
            GEMINI_URL.format(model=model), json=payload, headers=headers
        )
        if r.status_code in (400, 403):
            body = r.text[:300].lower()
            if "api key" in body or "api_key" in body or "key" in body:
                raise ValueError("API key de Gemini inválida o sin permisos")
            if "not found" in body or "not supported" in body:
                raise ValueError(f"Modelo '{model}' no disponible en tu cuenta")
            raise ValueError("La IA rechazó la petición, intenta de nuevo")
        if r.status_code == 404:
            raise ValueError(f"Modelo '{model}' no encontrado")
        if r.status_code == 429:
            raise ValueError("Cuota de Gemini agotada, intenta en un minuto")
        r.raise_for_status()
        data = r.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        content = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
    except (KeyError, IndexError, TypeError):
        # La IA puede bloquear por seguridad; informar sin romper
        try:
            reason = data.get("promptFeedback", {}).get("blockReason", "")
        except Exception:
            reason = ""
        if reason:
            raise ValueError("La IA bloqueó la descripción, reformúlala")
        raise ValueError("Respuesta inesperada del modelo")
    if not content.strip():
        raise ValueError("El modelo devolvió vacío, intenta de nuevo")
    return _extract_json(content)


# Palabras que delatan productos que NO son de construcción
# (el buscador a veces devuelve juguetes, juegos, etc.)
EXCLUIR_NOMBRE = (
    "juguete", "juego", "armatodo", "lego", "infantil", "niño", "niña",
    "bebé", "bebe", "mascota", "perro", "gato", "disfraz", "fiesta",
    "piñata", "pinata", "peluche", "muñeca", "muñeco", "carro control",
    "drone", "videojuego", "didact", "didáct", "armo", "maletin", "figuras",
    "rompecabezas", "puzzle", "libro", "cuento",
)
EXCLUIR_CATEGORIA = (
    "juguete", "juego", "didact", "infantil", "bebé", "bebe", "mascota",
    "fiesta", "disfraz", "deporte", "libro", "música", "musica", "hogar deco",
)


def _elegir_producto(products: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """Elige el mejor producto real de construcción, descartando juguetes y
    resultados que no contienen la búsqueda (incluyendo el número, ej "4")."""
    if not products:
        return {}
    tokens = [t for t in query.lower().split() if len(t) >= 1]

    def _categoria_real(p: Dict[str, Any]) -> bool:
        # Los productos hallados en páginas de categoría traen etiqueta real
        # ("Construcción", "Pintura"...); los de juguetería suelen venir solo
        # de la búsqueda genérica.
        cat = str(p.get("categoria", "")).strip().lower()
        return bool(cat) and not cat.startswith("búsqueda")

    def _pasa(p: Dict[str, Any], estricto: bool) -> bool:
        nombre = str(p.get("nombre", "")).lower()
        categoria = str(p.get("categoria", "")).lower()
        if any(w in categoria for w in EXCLUIR_CATEGORIA):
            return False
        if any(w in nombre for w in EXCLUIR_NOMBRE):
            return False
        if float(p.get("precio", 0) or 0) <= 0:
            return False
        if estricto and tokens and not all(t in nombre for t in tokens):
            return False
        return True

    # 1) Coincidencia exacta en categoría real de construcción
    for p in products:
        if _pasa(p, estricto=True) and _categoria_real(p):
            return p
    # 2) Coincidencia exacta en cualquier lado
    for p in products:
        if _pasa(p, estricto=True):
            return p
    # 3) Respaldo: primer producto con precio que no sea juguete
    for p in products:
        if _pasa(p, estricto=False):
            return p
    return {}


async def _precio_homecenter(nombre_busqueda: str) -> Dict[str, Any]:
    """Busca el mejor precio real en Homecenter. Nunca rompe el flujo."""
    from app.scrapers.homecenter import HomecenterScraper

    try:
        scraper = HomecenterScraper()
        products = await asyncio.wait_for(
            scraper.search_all_categories(nombre_busqueda), timeout=25
        )
        return _elegir_producto(products or [], nombre_busqueda)
    except Exception as e:
        print(f"[AI] Homecenter fail '{nombre_busqueda}': {e}")
        return {}


def _precio_tabulador(query: str) -> Dict[str, Any]:
    """Busca la tarea de mano de obra en el tabulador local."""
    from app.services.labor_service import search_labor

    try:
        tasks = search_labor(query)
        return tasks[0] if tasks else {}
    except Exception as e:
        print(f"[AI] Tabulador fail '{query}': {e}")
        return {}


async def analizar_obra(descripcion: str, tax_rate: float = 0.16) -> Dict[str, Any]:
    descripcion = (descripcion or "").strip()
    if len(descripcion) < 5:
        raise ValueError("Describe tu obra con un poco más de detalle")

    ai = await _call_model(descripcion)
    obra = ai.get("obra", {}) or {}
    materiales_ai: List[Dict[str, Any]] = ai.get("materiales", []) or []
    mano_ai: List[Dict[str, Any]] = ai.get("mano_de_obra", []) or []

    # Precios reales en paralelo (máx 4 búsquedas simultáneas)
    sem = asyncio.Semaphore(4)

    async def _mat(m: Dict[str, Any]) -> Dict[str, Any]:
        nombre = str(m.get("nombre_busqueda", "")).strip()[:60]
        cantidad = max(0.0, float(m.get("cantidad", 0) or 0))
        unidad = str(m.get("unidad", "unidad"))[:20] or "unidad"
        nota = str(m.get("nota", ""))[:200]
        async with sem:
            p = await _precio_homecenter(nombre)
        precio = float(p.get("precio", 0) or 0)
        return {
            "nombre_busqueda": nombre,
            "nombre": p.get("nombre", nombre.title()) if p else nombre.title(),
            "cantidad": cantidad,
            "unidad": unidad,
            "nota": nota,
            "precio": precio,
            "moneda": p.get("moneda", "COP") if p else "COP",
            "marca": p.get("marca", "") if p else "",
            "imagen_url": p.get("imagen_url", "") if p else "",
            "url_producto": p.get("url_producto", "") if p else "",
            "categoria": p.get("categoria", "") if p else "",
            "encontrado": bool(p and precio > 0),
            "subtotal": round(precio * cantidad, 2),
        }

    materiales = await asyncio.gather(*[_mat(m) for m in materiales_ai[:12]])

    mano = []
    for t in mano_ai[:8]:
        q = str(t.get("query_tabulador", "")).strip()[:60]
        cantidad = max(0.0, float(t.get("cantidad", 0) or 0))
        unidad = str(t.get("unidad", "m²"))[:10] or "m²"
        nota = str(t.get("nota", ""))[:200]
        task = _precio_tabulador(q)
        pu = float(task.get("precio_unitario", 0) or 0)
        mano.append({
            "query_tabulador": q,
            "nombre": task.get("nombre", q.title()) if task else q.title(),
            "cantidad": cantidad,
            "unidad": unidad or (task.get("unidad", "m²") if task else "m²"),
            "nota": nota,
            "precio_unitario": pu,
            "moneda": "COP",
            "categoria": task.get("categoria", "") if task else "",
            "encontrado": bool(task and pu > 0),
            "subtotal": round(pu * cantidad, 2),
        })

    sub_mat = round(sum(m["subtotal"] for m in materiales), 2)
    sub_mo = round(sum(t["subtotal"] for t in mano), 2)
    subtotal = round(sub_mat + sub_mo, 2)
    tax = round(subtotal * tax_rate, 2)

    advertencias = []
    sin_precio = [m["nombre_busqueda"] for m in materiales if not m["encontrado"]]
    if sin_precio:
        advertencias.append(
            "Sin precio en Homecenter: " + ", ".join(sin_precio)
            + ". Revísalos antes de enviar el presupuesto."
        )
    if (obra.get("confianza") or "") == "baja":
        advertencias.append(
            "La descripción no traía medidas claras; las cantidades son estimadas. Edítalas si es necesario."
        )

    return {
        "obra": {
            "tipo": str(obra.get("tipo", "General"))[:80] or "General",
            "descripcion": str(obra.get("descripcion", ""))[:300],
            "area_m2": obra.get("area_m2"),
            "medidas_usadas": str(obra.get("medidas_usadas", ""))[:200],
            "confianza": str(obra.get("confianza", "media"))[:10] or "media",
        },
        "materiales": materiales,
        "mano_de_obra": mano,
        "subtotal_materiales": sub_mat,
        "subtotal_mano_obra": sub_mo,
        "subtotal": subtotal,
        "tax_amount": tax,
        "total": round(subtotal + tax, 2),
        "advertencias": advertencias,
    }
