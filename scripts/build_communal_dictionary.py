#!/usr/bin/env python3
"""Build the machine-readable dictionary for the public integrated communal master."""

from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

MASTER = Path('data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv')
OUT_CSV = Path('data/metadata/communal_master_dictionary.csv')
OUT_MD = Path('docs/communal_master_dictionary.md')

KEY_META = {
    'region': ('Código de región', 'Censo/Atlas', 'territorio', 'código', 'Identificador numérico de región.'),
    'region_nombre': ('Región', 'Censo/Atlas', 'territorio', 'texto', 'Nombre de la región.'),
    'provincia': ('Código de provincia', 'Censo/Atlas', 'territorio', 'código', 'Identificador numérico de provincia.'),
    'provincia_nombre': ('Provincia', 'Censo/Atlas', 'territorio', 'texto', 'Nombre de la provincia.'),
    'comuna': ('Código de comuna', 'Censo/Atlas', 'territorio', 'código', 'Código territorial usado como llave principal del maestro.'),
    'comuna_nombre': ('Comuna', 'Censo/Atlas', 'territorio', 'texto', 'Nombre de la comuna.'),
}


def ookla_meta(col: str):
    if not col.startswith('ookla_'):
        return None
    if col in {'ookla_observed_any_2026q1', 'ookla_period', 'ookla_spatial_method'}:
        special = {
            'ookla_observed_any_2026q1': ('Observación Ookla disponible', 'sí/no', 'Indica si la comuna tiene observaciones fijas o móviles asignadas en Q1 2026.'),
            'ookla_period': ('Período Ookla', 'trimestre', 'Período de referencia de las métricas Ookla integradas.'),
            'ookla_spatial_method': ('Método espacial Ookla', 'texto', 'Regla espacial usada para asignar tiles a comunas.'),
        }
        label, unit, desc = special[col]
        return label, 'Ookla Open Data', 'test de red', unit, desc

    m = re.match(r'ookla_(fixed|mobile)_(.+)', col)
    if not m:
        return None
    net, metric = m.groups()
    net_es = 'fija' if net == 'fixed' else 'móvil'
    unit = 'número'
    label = f'Ookla {net_es} {metric}'
    description = f'Métrica de red {net_es} agregada desde tiles Ookla.'
    if 'download_mbps' in metric:
        unit, label = 'Mbps', f'Descarga Ookla {net_es}'
        description = f'Velocidad media de descarga de red {net_es}, ponderada por número de tests del tile.'
    elif 'upload_mbps' in metric:
        unit, label = 'Mbps', f'Carga Ookla {net_es}'
        description = f'Velocidad media de carga de red {net_es}, ponderada por número de tests del tile.'
    elif 'latency_ms' in metric and 'delta' not in metric:
        unit, label = 'ms', f'Latencia Ookla {net_es}'
        description = f'Latencia media de red {net_es}, ponderada por número de tests del tile.'
    elif 'loaded_latency' in metric:
        unit, label = 'ms', f'Latencia cargada Ookla {net_es}'
    elif 'delta_pct' in metric:
        unit, label = 'porcentaje', f'Variación trimestral Ookla {net_es}'
        description = f'Variación porcentual Q4 2025 a Q1 2026 para red {net_es}.'
    elif 'tests' in metric:
        unit, label = 'número', f'Tests Ookla {net_es}'
        description = f'Número de tests representados en los tiles asignados a la comuna para red {net_es}.'
    elif 'devices' in metric:
        unit, label = 'número', f'Dispositivos Ookla {net_es}'
        description = 'Suma de dispositivos reportados por tile. Puede contar un dispositivo en más de un tile y no representa usuarios únicos comunales.'
    elif 'tiles' in metric:
        unit, label = 'número', f'Tiles Ookla {net_es}'
        description = f'Número de tiles Ookla asignados espacialmente a la comuna para red {net_es}.'
    return label, 'Ookla Open Data', 'test de red', unit, description


def mobile_meta(col: str):
    if not (col.endswith('_point_records_2025m03') or col.endswith('_operators_present_2025m03')):
        return None
    operator_match = re.match(r'(claro|entel|movistar|wom)_(4g|5g)_point_records_2025m03', col)
    total_match = re.match(r'mobile_(4g|5g)_point_records_2025m03', col)
    operators_match = re.match(r'mobile_(4g|5g)_operators_present_2025m03', col)
    if operator_match:
        operator, tech = operator_match.groups()
        return f'Registros de red {tech.upper()} · {operator.title()}', 'SUBTEL ArcGIS marzo 2025', 'registro puntual de red', 'número', f'Número de registros puntuales públicos SUBTEL {tech.upper()} de {operator.title()} asignados espacialmente a la comuna. No equivale a torres físicas únicas ni a porcentaje de cobertura.'
    if total_match:
        tech = total_match.group(1).upper()
        return f'Registros de red {tech}', 'SUBTEL ArcGIS marzo 2025', 'registro puntual de red', 'número', f'Suma de registros puntuales públicos SUBTEL {tech} de Claro, Entel, Movistar y WOM asignados a la comuna. No representa torres únicas, población cubierta ni superficie cubierta.'
    if operators_match:
        tech = operators_match.group(1).upper()
        return f'Operadores con registros {tech}', 'SUBTEL ArcGIS marzo 2025', 'operador-red', '0–4', f'Número de operadores entre Claro, Entel, Movistar y WOM con al menos un registro puntual SUBTEL {tech} dentro de la comuna. Es presencia observable de registros de red, no una medida de cobertura efectiva.'
    return None


def education_meta(col: str):
    mapping = {
        'mineduc_aulas_selected_establishments_2025': ('Aulas Conectadas · establecimientos seleccionados', 'establecimiento', 'número', 'Número de RBD seleccionados en Aulas Conectadas 2025 asignados a la comuna mediante el Directorio oficial de Establecimientos Educacionales 2025.'),
        'mineduc_aulas_waitlist_establishments_2025': ('Aulas Conectadas · lista de espera', 'establecimiento', 'número', 'Número de RBD en lista de espera de Aulas Conectadas 2025 asignados a la comuna.'),
        'mineduc_aulas_selected_rural_establishments_2025': ('Aulas Conectadas · seleccionados rurales', 'establecimiento', 'número', 'Número de establecimientos seleccionados cuyo Directorio oficial 2025 los clasifica como rurales.'),
        'mineduc_aulas_selected_enrollment_2025': ('Matrícula de establecimientos seleccionados Aulas Conectadas', 'matrícula de establecimiento', 'estudiantes', 'Suma de MAT_TOTAL del Directorio oficial 2025 para establecimientos seleccionados. Describe el tamaño de los establecimientos y no equivale a estudiantes beneficiarios efectivos.'),
        'mineduc_aulas_selected_with_coordinates_2025': ('Aulas Conectadas · seleccionados con coordenadas', 'establecimiento', 'número', 'Número de establecimientos seleccionados con latitud y longitud disponibles en el Directorio oficial 2025.'),
    }
    if col not in mapping:
        return None
    label, stat_unit, unit, desc = mapping[col]
    return label, 'Mineduc Aulas Conectadas 2025', stat_unit, unit, desc


def fixed_access_meta(col: str):
    mapping = {
        'fixed_access_public_linework_length_km': ('Trazado público RedAcceso', 'trazado de red', 'km', 'Suma de longitud geodésica de capas públicas RedAcceso SUBTEL recortadas dentro de la comuna. Las capas pueden superponerse y no representan kilómetros físicos únicos ni cobertura de hogares.'),
        'fixed_access_public_layers_present': ('Capas públicas RedAcceso presentes', 'capa de red', 'número', 'Número de servicios públicos RedAcceso consultables con al menos un tramo lineal intersectando la comuna.'),
        'fixed_access_public_operators_present': ('Operadores con trazado RedAcceso público', 'operador-red', 'número', 'Número de operadores/entidades con al menos un trazado RedAcceso público consultable dentro de la comuna. No equivale a oferta comercial disponible para todos los hogares.'),
    }
    if col not in mapping:
        return None
    label, stat_unit, unit, desc = mapping[col]
    return label, 'SUBTEL ArcGIS RedAcceso', stat_unit, unit, desc


def fixed_subscription_meta(col: str):
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

def fallback_meta(col: str):
    if col in KEY_META:
        return KEY_META[col]
    if col == 'hogares_sin_internet_pct':
        return 'Hogares sin Internet', 'Censo/Atlas', 'hogar', 'porcentaje', 'Porcentaje de hogares válidos para Internet clasificados sin acceso.'
    if 'trampa_movil' in col:
        unit = 'porcentaje' if col.endswith('_pct') else 'número'
        return 'Dependencia móvil', 'Atlas derivado', 'hogar', unit, 'Proxy operacional de dependencia móvil. No es una categoría oficial del Censo.'
    if col.startswith('hogares_') or col.startswith('pct_'):
        unit = 'porcentaje' if col.endswith('_pct') or col.startswith('pct_') else 'número'
        return col.replace('_', ' ').title(), 'Censo/Atlas', 'hogar', unit, 'Variable agregada de hogar de la capa comunal pública.'
    if col == 'macrozona_operativa':
        return 'Macrozona operativa', 'Atlas derivado', 'territorio', 'categoría', 'Agrupación territorial descriptiva usada por el proyecto.'
    return col.replace('_', ' ').title(), 'Capa integrada', 'territorio', 'según variable', 'Campo de la capa comunal integrada; revisar documentación de origen.'


def denominator(col: str) -> str:
    if col == 'hogares_sin_internet_pct': return 'hogares_validos_internet'
    if col.endswith('_pct') or col.startswith('pct_'): return 'hogares_total o universo específico de la variable'
    if col.startswith('ookla_'): return 'tests del tile cuando corresponde a promedio ponderado'
    if col.endswith('_point_records_2025m03'): return 'conteo de registros puntuales asignados espacialmente'
    if col.endswith('_operators_present_2025m03'): return '4 operadores observados: Claro, Entel, Movistar y WOM'
    if col.startswith('mineduc_aulas_'): return 'registros administrativos de establecimientos RBD; Directorio oficial 2025 para territorialización'
    if col.startswith('fixed_access_public_'): return 'capas RedAcceso públicas y consultables en SUBTEL ArcGIS'
    if col == 'subtel_fixed_residential_per_100_censo_households_2026m03': return 'conexiones residenciales SUBTEL / hogares_total Censo 2024 × 100'
    if col.startswith('subtel_fixed_'): return 'registro administrativo SUBTEL; sin ponderación'
    return 'no aplica'


def comparison_note(col: str) -> str:
    if 'trampa_movil' in col: return 'Proxy del proyecto; no es categoría oficial censal.'
    if col.startswith('ookla_'): return 'Ookla observa tests realizados; no equivale a cobertura universal ni a una muestra probabilística de hogares.'
    if col.endswith('_point_records_2025m03') or col.endswith('_operators_present_2025m03'): return 'Registros puntuales de red publicados por SUBTEL. No deben interpretarse como torres únicas ni como porcentaje de cobertura geográfica o poblacional.'
    if col.startswith('mineduc_aulas_'): return 'Registro administrativo de participación/selección en un programa educativo. No equivale a conectividad efectiva instalada ni a acceso domiciliario de estudiantes.'
    if col.startswith('fixed_access_public_'): return 'Trazados regulatorios públicos. Las capas pueden superponerse; no equivalen a disponibilidad comercial, fibra hasta el hogar ni porcentaje de cobertura.'
    if col.startswith('subtel_fixed_'): return 'Conexiones administrativas no equivalen a hogares únicos ni a cobertura. La reconstrucción reconcilia 16 subtotales regionales para total y residencial; Antártica (12202) conserva una celda fuente explícitamente vacía.'
    return 'Variable agregada; revisar metodología de la capa de origen antes de comparar universos.'


def main() -> None:
    master = pd.read_csv(MASTER, nrows=5)
    previous = {}
    if OUT_CSV.exists():
        old = pd.read_csv(OUT_CSV, dtype=str).fillna('')
        previous = {row['variable']: row for row in old.to_dict('records')}

    rows = []
    for col in master.columns:
        meta = fixed_subscription_meta(col) or education_meta(col) or fixed_access_meta(col) or mobile_meta(col) or ookla_meta(col)
        if meta is None and col in previous:
            old = previous[col]
            meta = (old.get('label_es', col.replace('_', ' ').title()), old.get('source_layer', 'Capa integrada'), old.get('statistical_unit', 'territorio'), old.get('unit', 'según variable'), old.get('description', 'Campo de la capa comunal integrada.'))
        if meta is None:
            meta = fallback_meta(col)
        label, source, stat_unit, unit, description = meta
        rows.append({'variable': col, 'label_es': label, 'source_layer': source, 'statistical_unit': stat_unit, 'territorial_level': 'comuna', 'unit': unit, 'denominator_or_weight': denominator(col), 'description': description, 'comparability_note': comparison_note(col)})

    out = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    source_counts = out['source_layer'].value_counts().to_dict()
    text = [
        '# Diccionario del maestro comunal integrado','',
        f'El archivo documenta **{len(out)} variables** del maestro `chile_digital_inclusion_communes_2026_integrated.csv`.','',
        'La tabla canónica y legible por máquinas está en `data/metadata/communal_master_dictionary.csv`.','',
        '## Principios','',
        '- una fila del maestro representa una comuna',
        '- los porcentajes censales se mantienen separados de métricas de desempeño, registros de red y registros administrativos educativos',
        '- Ookla se interpreta como desempeño observado donde existieron tests, no como cobertura probabilística',
        '- los registros 4G/5G SUBTEL representan entidades puntuales publicadas por operador, no torres físicas únicas ni porcentaje de cobertura',
        '- RedAcceso representa trazados regulatorios públicos y no disponibilidad comercial universal',
        '- Aulas Conectadas representa selección administrativa de establecimientos y no conectividad efectiva del hogar',
        '- la dependencia móvil es una proxy operacional del proyecto y no una categoría oficial del Censo',
        '- no se publican ponderadores, scores ni el Índice de Vulnerabilidad Digital completo','',
        '## Variables por capa','',
    ]
    for source, count in source_counts.items(): text.append(f'- {source}: {count}')
    text += ['', '## Uso','', 'Antes de construir rankings o modelos, revisar `statistical_unit`, `denominator_or_weight` y `comparability_note`. No deben mezclarse mecánicamente hogares censales, personas ponderadas de encuesta, tests de red, trazados regulatorios y registros de establecimientos.','', 'Última revisión: 2026-08-14.']
    OUT_MD.write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(f'Wrote {len(out)} dictionary rows')

if __name__ == '__main__':
    main()
