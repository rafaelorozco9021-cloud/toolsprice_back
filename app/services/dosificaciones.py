"""Tabla de dosificación determinista para materiales de obra (Colombia).

La IA identifica el oficio y las medidas; ESTA tabla calcula las cantidades
exactas. Así los números son auditables y no dependen del modelo.

Fuentes: proporciones estándar de obra 1:4 para alistados, rendimientos
de mampostería/friso/pintura/enchape de uso común en Colombia.
"""
import math

# Mortero 1:4 (alistado): por cada m³ de mortero
CEMENTO_KG_POR_M3 = 350.0
ARENA_M3_POR_M3 = 1.05
AGUA_L_POR_M3 = 55.0
BULTO_KG = 50.0
# Concreto 1:2:3 (~3000 PSI, pisos/placas): por cada m³ de concreto
CONC_CEMENTO_KG_M3 = 350.0
CONC_ARENA_M3_M3 = 0.55
CONC_GRAVILLA_M3_M3 = 0.85
MALLA_M2_PANEL = 14.1  # panel 6 x 2.35 m

TIPOS = ("muro_bloque", "alistado", "friso", "pintura", "piso_ceramica",
         "concreto", "general")


def _ceil2(x: float) -> float:
    # Techo a 2 decimales, tolerando error de punto flotante (2.42, no 2.43)
    return math.ceil(x * 100 - 1e-9) / 100


def calcular_materiales(obra_tipo: str, area_m2: float, espesor_m: float | None = None):
    """Devuelve (materiales, notas). materiales: lista de dicts con
    nombre_busqueda/cantidad/unidad/nota. Cantidades exactas por tabla."""
    obra_tipo = (obra_tipo or "general").strip().lower()
    area = max(0.0, float(area_m2 or 0))
    notas: list[str] = []
    if obra_tipo == "alistado":
        e = float(espesor_m or 0.04)
        vol = area * e * 1.10  # +10% desperdicio
        kg = vol * CEMENTO_KG_POR_M3
        bultos = math.ceil(kg / BULTO_KG)
        arena = _ceil2(vol * ARENA_M3_POR_M3)
        agua = int(round(vol * AGUA_L_POR_M3))
        notas.append(
            f"Mortero 1:4, espesor {int(round(e * 100))} cm +10% desperdicio. "
            f"Agua aprox: {agua} L (se ajusta en obra a mezcla 'tierra húmeda')."
        )
        return ([
            {"nombre_busqueda": "cemento gris", "cantidad": float(bultos),
             "unidad": "bulto x 50kg",
             "nota": f"{int(round(kg))} kg para {round(vol, 2)} m³ de mortero"},
            {"nombre_busqueda": "arena lavada", "cantidad": arena,
             "unidad": "m³", "nota": "Arena de pega, limpia y sin arcilla"},
        ], notas)
    if obra_tipo == "muro_bloque":
        bloques = math.ceil(area * 14 * 1.08)  # 14 u/m² + 8%
        bultos = math.ceil(area / 4)  # 1 bulto rinde ~4 m²
        arena = _ceil2(area * 0.08)
        return ([
            {"nombre_busqueda": "bloque 4", "cantidad": float(bloques),
             "unidad": "unidad", "nota": "14 bloques/m² + 8% desperdicio"},
            {"nombre_busqueda": "cemento gris", "cantidad": float(bultos),
             "unidad": "bulto x 50kg", "nota": "Mortero de pega 1:4"},
            {"nombre_busqueda": "arena lavada", "cantidad": arena,
             "unidad": "m³", "nota": "0.08 m³ por m² de muro"},
        ], notas)
    if obra_tipo == "friso":
        bultos = math.ceil(area / 3)  # 1 bulto rinde ~3 m² a 1 cm
        arena = _ceil2(area * 0.03)
        return ([
            {"nombre_busqueda": "cemento gris", "cantidad": float(bultos),
             "unidad": "bulto x 50kg", "nota": "Pañete 1 cm, 1 bulto rinde ~3 m²"},
            {"nombre_busqueda": "arena lavada", "cantidad": arena,
             "unidad": "m³", "nota": "Arena fina para friso"},
        ], notas)
    if obra_tipo == "pintura":
        galones = math.ceil(area * 1.10 / 25)  # 1 galón rinde ~25 m² a 2 manos + 10%
        return ([
            {"nombre_busqueda": "pintura vinilo", "cantidad": float(galones),
             "unidad": "galón", "nota": "2 manos, 1 galón rinde ~25 m² + 10%"},
        ], notas)
    if obra_tipo == "piso_ceramica":
        m2 = _ceil2(area * 1.10)  # +10% cortes
        pegante = math.ceil(area / 5)  # 1 bulto 25 kg rinde ~5 m²
        fragua = _ceil2(area / 8)  # 1 kg rinde ~8 m²
        return ([
            {"nombre_busqueda": "piso ceramico", "cantidad": m2,
             "unidad": "m²", "nota": "Área + 10% por cortes y desperdicio"},
            {"nombre_busqueda": "pegante ceramica", "cantidad": float(pegante),
             "unidad": "bulto 25kg", "nota": "1 bulto rinde ~5 m²"},
            {"nombre_busqueda": "boquilla fragua", "cantidad": fragua,
             "unidad": "kg", "nota": "1 kg rinde ~8 m²"},
        ], notas)
    if obra_tipo == "concreto":
        # Piso/placa de concreto 1:2:3. Arena y gravilla a GRANEL (volqueta):
        # se devuelven en m³ sin precio web, con aviso al proveedor.
        e = float(espesor_m or 0.08)
        vol = area * e * 1.10  # +10% desperdicio
        kg = vol * CONC_CEMENTO_KG_M3
        bultos = math.ceil(kg / BULTO_KG)
        arena = _ceil2(vol * CONC_ARENA_M3_M3)
        gravilla = _ceil2(vol * CONC_GRAVILLA_M3_M3)
        paneles = math.ceil(area / MALLA_M2_PANEL) if area > 0 else 0
        notas.append(
            f"Concreto 1:2:3, espesor {int(round(e * 100))} cm +10% desperdicio. "
            "Arena y gravilla se piden a granel (volqueta)."
        )
        return ([
            {"nombre_busqueda": "cemento gris", "cantidad": float(bultos),
             "unidad": "bulto x 50kg",
             "nota": f"{int(round(kg))} kg para {round(vol, 2)} m³ de concreto"},
            {"nombre_busqueda": "arena lavada", "cantidad": arena,
             "unidad": "m³", "nota": "A granel (volqueta)", "granel": True},
            {"nombre_busqueda": "gravilla", "cantidad": gravilla,
             "unidad": "m³", "nota": "Piedra/granzón a granel (volqueta)",
             "granel": True},
            {"nombre_busqueda": "malla electrosoldada", "cantidad": float(paneles),
             "unidad": "panel", "nota": "Panel 6 x 2.35 m para refuerzo"},
        ], notas)
    return ([], notas)
