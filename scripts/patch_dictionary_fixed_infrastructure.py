#!/usr/bin/env python3
"""Keep fixed-subscription metadata aligned with the reconciled March-2026 source."""
from pathlib import Path

p = Path('scripts/build_communal_dictionary.py')
s = p.read_text(encoding='utf-8')

# Retain the historical bootstrap behavior for repositories that do not yet
# contain fixed_subscription_meta, but never reintroduce the superseded
# four-missing-communes interpretation.
if 'def fixed_subscription_meta' not in s:
    marker = '\ndef fallback_meta(col: str):\n'
    block = '''\ndef fixed_subscription_meta(col: str):
    mapping = {
        'subtel_fixed_connections_total_2026m03': ('Conexiones fijas totales SUBTEL', 'conexión administrativa', 'número', 'Número de conexiones de Internet fija reconstruidas para la comuna desde los bloques regionales reconciliados del workbook oficial SUBTEL de marzo de 2026.'),
        'subtel_fixed_connections_residential_2026m03': ('Conexiones fijas residenciales SUBTEL', 'conexión administrativa residencial', 'número', 'Número de conexiones residenciales de Internet fija reconstruidas para la comuna desde los bloques regionales reconciliados del workbook oficial SUBTEL de marzo de 2026.'),
        'subtel_fixed_residential_share_pct_2026m03': ('Participación residencial de conexiones fijas', 'conexión administrativa', 'porcentaje', 'Proporción de conexiones fijas comunales clasificadas como residenciales en la reconstrucción reconciliada de la fuente administrativa SUBTEL.'),
        'subtel_fixed_residential_per_100_censo_households_2026m03': ('Conexiones fijas residenciales por 100 hogares censales', 'conexión administrativa / hogar censal', 'razón por 100 hogares', 'Razón entre conexiones fijas residenciales SUBTEL de marzo de 2026 y hogares del Censo 2024. Es una intensidad administrativa descriptiva, no una tasa de cobertura y puede superar 100.'),
        'subtel_fixed_source_status_2026m03': ('Estado de reporte SUBTEL fijo', 'fuente administrativa', 'categoría', 'Indica si la reconstrucción comunal dispone de valor numérico de fuente. Antártica (12202) conserva una celda fuente explícitamente vacía como source_blank; no se imputa como cero.'),
    }
    if col not in mapping:
        return None
    label, stat_unit, unit, desc = mapping[col]
    return label, 'SUBTEL conexiones fijas marzo 2026', stat_unit, unit, desc
'''
    if marker not in s:
        raise SystemExit('fallback marker not found')
    s = s.replace(marker, block + marker, 1)

old_route = "meta = education_meta(col) or fixed_access_meta(col) or mobile_meta(col) or ookla_meta(col)"
new_route = "meta = fixed_subscription_meta(col) or education_meta(col) or fixed_access_meta(col) or mobile_meta(col) or ookla_meta(col)"
if old_route in s:
    s = s.replace(old_route, new_route, 1)

replacements = {
    "Número de conexiones de Internet fija reportadas por SUBTEL para la comuna en marzo de 2026.":
        "Número de conexiones de Internet fija reconstruidas para la comuna desde los bloques regionales reconciliados del workbook oficial SUBTEL de marzo de 2026.",
    "Número de conexiones residenciales de Internet fija reportadas por SUBTEL para la comuna en marzo de 2026.":
        "Número de conexiones residenciales de Internet fija reconstruidas para la comuna desde los bloques regionales reconciliados del workbook oficial SUBTEL de marzo de 2026.",
    "Proporción de conexiones fijas comunales clasificadas como residenciales en la fuente administrativa SUBTEL.":
        "Proporción de conexiones fijas comunales clasificadas como residenciales en la reconstrucción reconciliada de la fuente administrativa SUBTEL.",
    "Indica si la hoja comunal oficial SUBTEL reporta la comuna. Los casos no reportados se mantienen como faltantes y no se imputan como cero.":
        "Indica si la reconstrucción comunal dispone de valor numérico de fuente. Antártica (12202) conserva una celda fuente explícitamente vacía como source_blank; no se imputa como cero.",
    "Conexiones administrativas no equivalen a hogares únicos ni a cobertura. Cuatro comunas no son reportadas en la hoja fuente de marzo de 2026 y permanecen como faltantes.":
        "Conexiones administrativas no equivalen a hogares únicos ni a cobertura. La reconstrucción reconcilia 16 subtotales regionales para total y residencial; Antártica (12202) conserva una celda fuente explícitamente vacía.",
}
for old, new in replacements.items():
    s = s.replace(old, new)

# Ensure denominator routing exists.
needle = "    if col.startswith('fixed_access_public_'): return 'capas RedAcceso públicas y consultables en SUBTEL ArcGIS'\n"
if "subtel_fixed_residential_per_100_censo_households_2026m03'" not in s[s.find('def denominator'):s.find('def comparison_note')]:
    if needle not in s:
        raise SystemExit('denominator marker not found')
    s = s.replace(
        needle,
        needle + "    if col == 'subtel_fixed_residential_per_100_censo_households_2026m03': return 'conexiones residenciales SUBTEL / hogares_total Censo 2024 × 100'\n    if col.startswith('subtel_fixed_'): return 'registro administrativo SUBTEL; sin ponderación'\n",
        1,
    )

required = [
    'fixed_subscription_meta(col)',
    'Antártica (12202)',
    'bloques regionales reconciliados',
]
missing = [item for item in required if item not in s]
if missing:
    raise SystemExit(f'dictionary builder fixed-subscription metadata incomplete: {missing}')

p.write_text(s, encoding='utf-8')
print('dictionary builder aligned with reconciled SUBTEL fixed subscriptions')
