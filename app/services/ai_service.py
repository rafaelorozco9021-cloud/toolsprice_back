"""Agente IA que analiza la descripción de una obra y la convierte en
materiales + mano de obra con precios reales.

Proveedor: Google AI Studio (Gemini) vía generateContent.
Flujo: descripción -> modelo (JSON estricto) -> Homecenter (precios reales)
-> tabulador (precios mano de obra) -> presupuesto listo para el carrito.
"""
import asyncio
import json
import math
import re
from typing import Any, Dict, List

import httpx

from app.core.config import settings

SYSTEM_PROMPT = """Eres un maestro de obra colombiano con 20 años de experiencia en construcción,
pintura, plomería, soldadura y remodelación. Analizas la descripción de una obra
y devuelves ÚNICAMENTE un JSON válido, sin texto antes ni después, sin markdown.

Reglas de identificación (tú NO calculas cantidades de materiales: el sistema
usa tabla fija de dosificación. Tú solo identificas el oficio y las medidas):
- "obra_tipo_clave": UNA de muro_bloque | alistado | friso | pintura |
  piso_ceramica | concreto | general. "Plantilla" = alistado (mortero de
  nivelación, NO cerámica salvo que la pidan). Muro/ladrillo/bloque =
  muro_bloque. Pintar = pintura ("pintura tipo A" significa Tipo 1: vinilo
  interior premium a 2 manos; búscala como "pintura vinilo tipo 1"). Enchape/cerámica/porcelanato = piso_ceramica.
  Piso/placa de concreto, losa, contrapiso en concreto = concreto. Pañete/
  friso/revoque = friso. Si no encaja en ninguno, usa "general".
- Nombres para buscar en Homecenter (úsalos tal cual): el acero es "varilla
  corrugada" (ej "varilla corrugada 1/2" para media, "varilla corrugada 3/4"
  para tres cuartos; "cabilla" significa lo mismo pero NO lo uses para buscar).
  La piedra del concreto es "gravilla" (NO "piedra triturada", eso trae piedra
  decorativa). La malla es "malla electrosoldada".
- "area_m2": área total en m² (ancho × alto/largo).
- "espesor_m": SOLO para alistado si lo mencionan (ej 4 cm → 0.04). Si no lo
  dicen, omítelo (se asume 4 cm).
- "materiales": lista con "nombre_busqueda" corto (1-3 palabras) y "nota" de
  uso. La cantidad la calcula el sistema: pon 0. SOLO si el tipo es "general"
  estima tú cantidades razonables (esas sí se usan directo).
- Acero/varilla: solo si la obra lo exige (concreto, columnas, vigas, zapatas,
  losas). Para concreto usa "varilla corrugada 1/2" o "malla electrosoldada".
  Para un muro simple divisorio NO incluyas varilla, indica por qué en "nota".
- "query_tabulador": oficio del tabulador. Usa ESTOS valores: muro bloque →
  "muro bloque"; alistado/plantilla → "alistado"; friso → "friso"; pintura →
  "pintura"; cerámica/porcelanato → "piso ceramica"; concreto/placa/losa →
  "placa contrapiso"; plomería → "plomeria"; eléctrico → "punto electrico";
  soldadura → "soldadura".
- "cantidad" de mano de obra = área en la unidad del oficio (m², punto, ml).
- NUNCA inventes precios. Solo identificación, medidas y notas.
- Si la descripción no trae medidas, estima lo mínimo razonable y pon
  "confianza": "baja"; si trae medidas claras, "confianza": "alta".

Formato EXACTO de respuesta (JSON):
{
  "obra": {"tipo": "Mampostería", "obra_tipo_clave": "muro_bloque",
           "descripcion": "...", "area_m2": 7.5, "espesor_m": null,
           "medidas_usadas": "3.00 m de ancho x 2.50 m de alto", "confianza": "alta"},
  "materiales": [
    {"nombre_busqueda": "bloque 4", "cantidad": 0, "unidad": "unidad",
     "nota": "Muro bloque #4"}
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
            # El razonamiento interno consume del presupuesto de salida:
            # techo alto + pensamiento limitado para que el JSON salga completo
            "maxOutputTokens": 4096,
            "thinkingConfig": {"thinkingBudget": 1024},
            "responseMimeType": "application/json",
        },
    }
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(60.0, connect=10.0)
    ultimo_error = ""
    # 2 intentos: a veces el modelo corta o ensucia el JSON
    for intento in range(2):
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
        try:
            data = r.json()
            parts = data["candidates"][0]["content"]["parts"]
            content = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
            if not content.strip():
                raise ValueError("vacío")
            parsed = _extract_json(content)
            # Validar estructura mínima antes de aceptar
            if not isinstance(parsed, dict) or "materiales" not in parsed:
                raise ValueError("incompleto")
            return parsed
        except ValueError as e:
            ultimo_error = str(e)
            print(f"[AI] intento {intento + 1} respuesta inválida: {ultimo_error[:120]}")
            continue
    # La IA puede bloquear por seguridad; informar sin romper
    raise ValueError("La IA no devolvió un análisis válido, intenta de nuevo")


# Bultos de 40 kg por m³ según práctica de obra (regla del maestro).
# Ej: 3 m³ de gravilla = 200 bultos. Para el resto se usa densidad.
BULTOS_POR_M3 = (
    ("gravilla", 200.0 / 3.0),
    ("grava", 200.0 / 3.0),
)
DENSIDAD_KG_M3 = (
    ("grava", 1600.0), ("gravilla", 1600.0), ("triturado", 1600.0),
    ("piedra", 1600.0), ("recebo", 1700.0), ("balastro", 1700.0),
    ("arena", 1500.0),
)
PACK_KG_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*kg", re.IGNORECASE)


def _a_bultos(m: Dict[str, Any]) -> Dict[str, Any]:
    """Si la cantidad viene en m³ pero el producto se vende empacado (bulto),
    convierte a bultos para que cantidad × precio sea correcto."""
    if m.get("unidad") not in ("m³", "m3") or not m.get("encontrado"):
        return m
    nombre = str(m.get("nombre", ""))
    if not any(k in nombre.lower() for k in ("kg", "bulto", "bolsa", "saco")):
        return m
    mm = PACK_KG_RE.search(nombre)
    if not mm:
        return m
    pack_kg = float(mm.group(1).replace(",", "."))
    if pack_kg <= 0:
        return m
    q = str(m.get("nombre_busqueda", "")).lower()
    m3 = float(m.get("cantidad", 0) or 0)
    # Regla del maestro (bultos por m³) tiene prioridad sobre densidad
    bultos = None
    for kw, ratio in BULTOS_POR_M3:
        if kw in q:
            bultos = math.ceil(m3 * ratio)
            base_txt = f"{m3} m³ a {ratio:.1f} bultos/m³"
            break
    if bultos is None:
        dens = 1500.0
        for kw, d in DENSIDAD_KG_M3:
            if kw in q:
                dens = d
                break
        bultos = math.ceil(m3 * dens / pack_kg)
        base_txt = f"{m3} m³"
    m = dict(m)
    pack_txt = str(int(pack_kg) if pack_kg == int(pack_kg) else pack_kg)
    m["cantidad"] = float(bultos)
    m["unidad"] = f"bulto {pack_txt}kg"
    m["nota"] = (f"{base_txt} ≈ {bultos} bultos de {pack_txt} kg. "
                 "Si la pides por volqueta, edita cantidad y precio.")
    m["subtotal"] = round(float(m.get("precio", 0) or 0) * bultos, 2)
    m["aviso_granel"] = True
    return m
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
# Empaques múltiples ("Set x 12", "Pack x 6"): el precio es del paquete y
# rompe el cálculo por unidad. Se aceptan solo si no hay otra opción.
# (No confundir con medidas: "x 6m", "60x60" sí son válidas.)
import re as _re
PACK_RE = _re.compile(r"\b(set|pack|caja|combo|kit)\s*x\b", re.IGNORECASE)


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

    # 1) Coincidencia exacta en categoría real de construcción (sin empaques)
    for p in products:
        if _pasa(p, estricto=True) and _categoria_real(p) \
                and not PACK_RE.search(str(p.get("nombre", ""))):
            return p
    # 2) Coincidencia exacta en cualquier lado (sin empaques)
    for p in products:
        if _pasa(p, estricto=True) \
                and not PACK_RE.search(str(p.get("nombre", ""))):
            return p
    # 3) Respaldo: primer producto con precio que no sea juguete (acepta packs)
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

    # Cantidades por TABLA fija cuando se reconoce el oficio; la IA solo
    # identifica y mide. Si el oficio es desconocido ("general"), se usan
    # las cantidades estimadas por la IA.
    from app.services.dosificaciones import calcular_materiales, TIPOS
    tipo = str(obra.get("obra_tipo_clave", "general") or "general").strip().lower()
    area = obra.get("area_m2")
    try:
        area_f = float(area) if area is not None else 0.0
    except (TypeError, ValueError):
        area_f = 0.0
    espesor = obra.get("espesor_m")
    try:
        espesor_f = float(espesor) if espesor is not None else None
    except (TypeError, ValueError):
        espesor_f = None
    tabla_notas: list[str] = []
    if tipo in TIPOS and tipo != "general" and area_f > 0:
        materiales_ai, tabla_notas = calcular_materiales(tipo, area_f, espesor_f)

    # Precios reales en paralelo (máx 4 búsquedas simultáneas)
    sem = asyncio.Semaphore(4)

    async def _mat(m: Dict[str, Any]) -> Dict[str, Any]:
        nombre = str(m.get("nombre_busqueda", "")).strip()[:60]
        cantidad = max(0.0, float(m.get("cantidad", 0) or 0))
        unidad = str(m.get("unidad", "unidad"))[:20] or "unidad"
        nota = str(m.get("nota", ""))[:200]
        # Material a granel (arena/gravilla por volqueta): no tiene precio web,
        # se deja con precio 0 y aviso para cotizar con el proveedor
        if m.get("granel"):
            return {
                "nombre_busqueda": nombre,
                "nombre": nombre.title() + " (a granel)",
                "cantidad": cantidad,
                "unidad": unidad,
                "nota": nota + " Cotizar por volqueta con el proveedor.",
                "precio": 0,
                "moneda": "COP",
                "marca": "",
                "imagen_url": "",
                "url_producto": "",
                "categoria": "",
                "encontrado": False,
                "subtotal": 0,
            }
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

    materiales = [_a_bultos(m) for m in
                  await asyncio.gather(*[_mat(m) for m in materiales_ai[:12]])]

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
    advertencias.extend(tabla_notas)
    # La arena/grava se calcula en m³ pero en Homecenter se vende por bulto:
    # ya viene convertida a bultos; avisar que por volqueta sale más barata
    for m in materiales:
        if m.get("aviso_granel"):
            advertencias.append(
                f"OJO con '{m['nombre_busqueda']}': se cotizó por bulto "
                f"({int(m['cantidad'])} bultos). En obra suele pedirse por m³ "
                "(volqueta) con el proveedor: verifica ese precio."
            )
            break
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
