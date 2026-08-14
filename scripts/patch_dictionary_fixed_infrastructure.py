#!/usr/bin/env python3
from pathlib import Path
p=Path('scripts/build_communal_dictionary.py')
s=p.read_text(encoding='utf-8')
if 'def fixed_subscription_meta' not in s:
    marker='\ndef fallback_meta(col: str):\n'
    block='''\ndef fixed_subscription_meta(col: str):
    mapping = {
        'subtel_fixed_connections_total_2026m03': ('Conexiones fijas totales SUBTEL', 'conexión administrativa', 'número', 'Número de conexiones de Internet fija reportadas por SUBTEL para la comuna en marzo de 2026.'),
        'subtel_fixed_connections_residential_2026m03': ('Conexiones fijas residenciales SUBTEL', 'conexión administrativa residencial', 'número', 'Número de conexiones residenciales de Internet fija reportadas por SUBTEL para la comuna en marzo de 2026.'),
        'subtel_fixed_residential_share_pct_2026m03': ('Participación residencial de conexiones fijas', 'conexión administrativa', 'porcentaje', 'Proporción de conexiones fijas comunales clasificadas como residenciales en la fuente administrativa SUBTEL.'),
        'subtel_fixed_residential_per_100_censo_households_2026m03': ('Conexiones fijas residenciales por 100 hogares censales', 'conexión administrativa / hogar censal', 'razón por 100 hogares', 'Razón entre conexiones fijas residenciales SUBTEL de marzo de 2026 y hogares del Censo 2024. Es una intensidad administrativa descriptiva, no una tasa de cobertura y puede superar 100.'),
        'subtel_fixed_source_status_2026m03': ('Estado de reporte SUBTEL fijo', 'fuente administrativa', 'categoría', 'Indica si la hoja comunal oficial SUBTEL reporta la comuna. Los casos no reportados se mantienen como faltantes y no se imputan como cero.'),
    }
    if col not in mapping:
        return None
    label, stat_unit, unit, desc = mapping[col]
    return label, 'SUBTEL conexiones fijas marzo 2026', stat_unit, unit, desc
'''
    if marker not in s: raise SystemExit('fallback marker not found')
    s=s.replace(marker,block+marker,1)
old="meta = education_meta(col) or fixed_access_meta(col) or mobile_meta(col) or ookla_meta(col)"
new="meta = fixed_subscription_meta(col) or education_meta(col) or fixed_access_meta(col) or mobile_meta(col) or ookla_meta(col)"
if old in s:
    s=s.replace(old,new,1)
elif 'fixed_subscription_meta(col)' not in s:
    raise SystemExit('meta routing marker not found')
# enrich denominator and comparison functions without rewriting their whole bodies
needle="    if col.startswith('fixed_access_public_'): return 'capas RedAcceso públicas y consultables en SUBTEL ArcGIS'\n"
if "subtel_fixed_residential_per_100_censo_households_2026m03'" not in s[s.find('def denominator'):s.find('def comparison_note')]:
    if needle not in s: raise SystemExit('denominator marker not found')
    s=s.replace(needle,needle+"    if col == 'subtel_fixed_residential_per_100_censo_households_2026m03': return 'conexiones residenciales SUBTEL / hogares_total Censo 2024 × 100'\n    if col.startswith('subtel_fixed_'): return 'registro administrativo SUBTEL; sin ponderación'\n",1)
needle2="    if col.startswith('fixed_access_public_'): return 'Trazados regulatorios públicos. Las capas pueden superponerse; no equivalen a disponibilidad comercial, fibra hasta el hogar ni porcentaje de cobertura.'\n"
if "Conexiones administrativas no equivalen" not in s:
    if needle2 not in s: raise SystemExit('comparison marker not found')
    s=s.replace(needle2,needle2+"    if col.startswith('subtel_fixed_'): return 'Conexiones administrativas no equivalen a hogares únicos ni a cobertura. Cuatro comunas no son reportadas en la hoja fuente de marzo de 2026 y permanecen como faltantes.'\n",1)
p.write_text(s,encoding='utf-8')
print('dictionary builder patched for SUBTEL fixed subscriptions')
