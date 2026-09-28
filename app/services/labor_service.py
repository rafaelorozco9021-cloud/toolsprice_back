# Tabulador Mano de Obra Colombia 2026 - precios por m2 / punto / ml
# Fuente: promedios del mercado ferretero y revistas de construcción (Construdata, Camacol)
# Todos los valores en COP, solo mano de obra (no incluye material salvo indicado)

LABOR_CATALOG = [
    # Friso / Revoque
    {"id": "lab-001", "nombre": "Friso liso interior (pañete) 1cm", "categoria": "Friso", "descripcion": "Aplicación de mortero 1:4, plomado y reglado", "unidad": "m²", "precio_unitario": 18000, "rendimiento": "1.2 m²/h", "incluye_material": False},
    {"id": "lab-002", "nombre": "Friso liso exterior impermeabilizado", "categoria": "Friso", "descripcion": "Mortero 1:3 con Sika-1, curado 7 días", "unidad": "m²", "precio_unitario": 25000, "rendimiento": "1.0 m²/h", "incluye_material": False},
    {"id": "lab-003", "nombre": "Friso rustico / graniplast", "categoria": "Friso", "descripcion": "Acabado rústico con llana", "unidad": "m²", "precio_unitario": 22000, "rendimiento": "0.9 m²/h", "incluye_material": False},
    # Piso cerámica
    {"id": "lab-010", "nombre": "Instalación piso cerámica 30x30 (pega + fragua)", "categoria": "Piso cerámica", "descripcion": "Pegamento cerámico y boquilla, sin material", "unidad": "m²", "precio_unitario": 24000, "rendimiento": "2.5 m²/día", "incluye_material": False},
    {"id": "lab-011", "nombre": "Instalación porcelanato 60x60 rectificado", "categoria": "Piso cerámica", "descripcion": "Requiere nivelación previa", "unidad": "m²", "precio_unitario": 38000, "rendimiento": "2.0 m²/día", "incluye_material": False},
    {"id": "lab-012", "nombre": "Instalación piso porcelanato gran formato 80x80", "categoria": "Piso cerámica", "descripcion": "Con clips de nivelación", "unidad": "m²", "precio_unitario": 45000, "rendimiento": "1.5 m²/día", "incluye_material": False},
    {"id": "lab-013", "nombre": "Guardaescoba cerámica", "categoria": "Piso cerámica", "descripcion": "Pegado y fraguado perimetral", "unidad": "ml", "precio_unitario": 6000, "rendimiento": "15 ml/día", "incluye_material": False},
    # Enchape muro
    {"id": "lab-014", "nombre": "Enchape muro baño/cocina 20x30", "categoria": "Enchape", "descripcion": "Incluye cortes y dilataciones", "unidad": "m²", "precio_unitario": 28000, "rendimiento": "2.0 m²/día", "incluye_material": False},
    {"id": "lab-015", "nombre": "Enchape fachada ladrillo a la vista", "categoria": "Enchape", "descripcion": "Con junta de 1cm", "unidad": "m²", "precio_unitario": 35000, "rendimiento": "1.8 m²/día", "incluye_material": False},
    # Mampostería
    {"id": "lab-020", "nombre": "Muro bloque #4 (10x20x40) pegado", "categoria": "Mampostería", "descripcion": "Mortero 1:4, incluye andamio bajo", "unidad": "m²", "precio_unitario": 28000, "rendimiento": "3.0 m²/día", "incluye_material": False},
    {"id": "lab-021", "nombre": "Muro ladrillo H-10 a la vista", "categoria": "Mampostería", "descripcion": "Con alineación y junta", "unidad": "m²", "precio_unitario": 42000, "rendimiento": "2.5 m²/día", "incluye_material": False},
    {"id": "lab-022", "nombre": "Muro ladrillo prensado", "categoria": "Mampostería", "descripcion": "Acabado caravista", "unidad": "m²", "precio_unitario": 48000, "rendimiento": "2.0 m²/día", "incluye_material": False},
    # Pintura
    {"id": "lab-030", "nombre": "Pintura vinilo interior 2 manos (Tipo 1)", "categoria": "Pintura", "descripcion": "Incluye resane y lijado", "unidad": "m²", "precio_unitario": 8500, "rendimiento": "25 m²/día", "incluye_material": False},
    {"id": "lab-031", "nombre": "Pintura vinilo exterior acrílica 2 manos", "categoria": "Pintura", "descripcion": "Incluye sellador", "unidad": "m²", "precio_unitario": 12000, "rendimiento": "20 m²/día", "incluye_material": False},
    {"id": "lab-032", "nombre": "Estuco + Pintura interior 3 manos", "categoria": "Pintura", "descripcion": "Estucado plástico y vinilo", "unidad": "m²", "precio_unitario": 14500, "rendimiento": "12 m²/día", "incluye_material": False},
    {"id": "lab-033", "nombre": "Pintura epóxica piso", "categoria": "Pintura", "descripcion": "2 capas con imprimación", "unidad": "m²", "precio_unitario": 28000, "rendimiento": "15 m²/día", "incluye_material": False},
    # Placa / contrapiso
    {"id": "lab-040", "nombre": "Placa contrapiso e=4cm mortero 1:3", "categoria": "Pisos base", "descripcion": "Nivelación para enchape", "unidad": "m²", "precio_unitario": 20000, "rendimiento": "8 m²/día", "incluye_material": False},
    {"id": "lab-041", "nombre": "Alistado piso con mortero autonivelante 2cm", "categoria": "Pisos base", "descripcion": "Para porcelanato gran formato", "unidad": "m²", "precio_unitario": 18000, "rendimiento": "10 m²/día", "incluye_material": False},
    # Plomería / Gas
    {"id": "lab-050", "nombre": "Punto hidráulico agua fría 1/2 PVC", "categoria": "Plomería", "descripcion": "Tubería pavco + accesorios, prueba presión", "unidad": "punto", "precio_unitario": 75000, "rendimiento": "4 p/día", "incluye_material": False},
    {"id": "lab-051", "nombre": "Punto sanitario PVC 2/3/4", "categoria": "Plomería", "descripcion": "Desagüe con pendiente 2%", "unidad": "punto", "precio_unitario": 80000, "rendimiento": "3 p/día", "incluye_material": False},
    {"id": "lab-052", "nombre": "Instalación grifería / sanitario", "categoria": "Plomería", "descripcion": "Montaje y sello", "unidad": "punto", "precio_unitario": 60000, "rendimiento": "5 p/día", "incluye_material": False},
    {"id": "lab-053", "nombre": "Red gas domiciliaria punto", "categoria": "Plomería", "descripcion": "Tubería cobre + prueba hermeticidad", "unidad": "punto", "precio_unitario": 95000, "rendimiento": "2 p/día", "incluye_material": False},
    # Eléctrico
    {"id": "lab-060", "nombre": "Punto eléctrico toma/interruptor (tub. PVC)", "categoria": "Eléctrico", "descripcion": "Cableado 12 AWG, caja y aparato", "unidad": "punto", "precio_unitario": 65000, "rendimiento": "6 p/día", "incluye_material": False},
    {"id": "lab-061", "nombre": "Punto iluminación techo + roseta", "categoria": "Eléctrico", "descripcion": "Incluye soquetería", "unidad": "punto", "precio_unitario": 55000, "rendimiento": "8 p/día", "incluye_material": False},
    {"id": "lab-062", "nombre": "Acometida tablero 6 circuitos", "categoria": "Eléctrico", "descripcion": "Breakers, barraje, peinado", "unidad": "global", "precio_unitario": 450000, "rendimiento": "1 día", "incluye_material": False},
    # Cubierta
    {"id": "lab-070", "nombre": "Instalación teja termoacústica", "categoria": "Cubierta", "descripcion": "Estructura metálica no incluida", "unidad": "m²", "precio_unitario": 18000, "rendimiento": "12 m²/día", "incluye_material": False},
    {"id": "lab-071", "nombre": "Instalación cielo raso PVC", "categoria": "Cubierta", "descripcion": "Con estructura aluminio", "unidad": "m²", "precio_unitario": 32000, "rendimiento": "8 m²/día", "incluye_material": False},
    # Soldadura / Herrería
    {"id": "lab-080", "nombre": "Estructura metálica soldada (tubo/ángulo)", "categoria": "Soldadura", "descripcion": "Soldadura MIG, pulido", "unidad": "kg", "precio_unitario": 4500, "rendimiento": "15 kg/día", "incluye_material": False},
    {"id": "lab-081", "nombre": "Reja / ventana soldada instalada", "categoria": "Soldadura", "descripcion": "Anticorrosivo + pintura", "unidad": "m²", "precio_unitario": 85000, "rendimiento": "1.5 m²/día", "incluye_material": False},
]

from rapidfuzz import fuzz

def search_labor(query: str, categoria: str | None = None):
    q = (query or "").lower().strip()
    tokens = [t for t in q.split() if t] if q else []
    res = []
    for it in LABOR_CATALOG:
        if categoria and categoria.lower() not in it["categoria"].lower() and categoria.lower() not in it["nombre"].lower():
            # si filtra por categoria exacta, descartar otras
            if categoria.lower() not in ("todas", "todos"):
                if categoria.lower() != it["categoria"].lower():
                    continue
        if not tokens:
            res.append({**it, "_score": 0})
            continue
        text = f"{it['nombre']} {it['categoria']} {it['descripcion']}".lower()
        matched = sum(1 for tok in tokens if tok in text)
        if matched == 0:
            # fuzzy fallback
            score = fuzz.partial_ratio(q, text)
            if score < 60:
                continue
            res.append({**it, "_score": score})
        else:
            score = fuzz.partial_ratio(q, text) + matched*20
            res.append({**it, "_score": score})
    res.sort(key=lambda x: x.get("_score", 0), reverse=True)
    for r in res:
        r.pop("_score", None)
    return res

def list_categorias():
    cats = sorted(set(it["categoria"] for it in LABOR_CATALOG))
    return cats
