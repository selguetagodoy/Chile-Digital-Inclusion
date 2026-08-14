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
        label = f'Registros de red {tech.upper()} · {operator.title()}'
        desc = f'Número de registros puntuales públicos SUBTEL {tech.upper()} de {operator.title()} asignados espacialmente a la comuna. No equivale a torres físicas únicas ni a porcentaje de cobertura.'
        return label, 'SUBTEL ArcGIS marzo 2025', 'registro puntual de red', 'número', desc

    if total_match:
        tech = total_match.group(1).upper()
        label = f'Registros de red {tech}'
        desc = f'Suma de registros puntuales públicos SUBTEL {tech} de Claro, Entel, Movistar y WOM asignados a la comuna. No representa torres únicas, población cubierta ni superficie cubierta.'
        return label, 'SUBTEL ArcGIS marzo 2025', 'registro puntual de red', 'número', desc

    if operators_match:
        tech = operators_match.group(1).upper()
        label = f'Operadores con registros {tech}'
        desc = f'Número de operadores entre Claro, Entel, Movistar y WOM con al menos un registro puntual SUBTEL {tech} dentro de la comuna. Es presencia observable de registros de red, no una medida de cobertura efectiva.'
        return label, 'SUBTEL ArcGIS marzo 2025', 'operador-red', '0–4', desc
    return None


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
    if col == 'hogares_sin_internet_pct':
        return 'hogares_validos_internet'
    if col.endswith('_pct') or col.startswith('pct_'):
        return 'hogares_total o universo específico de la variable'
    if col.startswith('ookla_'):
        return 'tests del tile cuando corresponde a promedio ponderado'
    if col.endswith('_point_records_2025m03'):
        return 'conteo de registros puntuales asignados espacialmente'
    if col.endswith('_operators_present_2025m03'):
        return '4 operadores observados: Claro, Entel, Movistar y WOM'
    return 'no aplica'


def comparison_note(col: str) -> str:
    if 'trampa_movil' in col:
        return 'Proxy del proyecto; no es categoría oficial censal.'
    if col.startswith('ookla_'):
        return 'Ookla observa tests realizados; no equivale a cobertura universal ni a una muestra probabilística de hogares.'
    if col.endswith('_point_records_2025m03') or col.endswith('_operators_present_2025m03'):
        return 'Registros puntuales de red publicados por SUBTEL. No deben interpretarse como torres únicas ni como porcentaje de cobertura geográfica o poblacional.'
    return 'Variable agregada; revisar metodología de la capa de origen antes de comparar universos.'


def main() -> None:
    master = pd.read_csv(MASTER, nrows=5)

    # Preserve richer descriptions already published for existing variables.
    previous = {}
    if OUT_CSV.exists():
        old = pd.read_csv(OUT_CSV, dtype=str).fillna('')
        previous = {row['variable']: row for row in old.to_dict('records')}

    rows = []
    for col in master.columns:
        meta = mobile_meta(col) or ookla_meta(col)
        if meta is None and col in previous:
            old = previous[col]
            meta = (
                old.get('label_es', col.replace('_', ' ').title()),
                old.get('source_layer', 'Capa integrada'),
                old.get('statistical_unit', 'territorio'),
                old.get('unit', 'según variable'),
                old.get('description', 'Campo de la capa comunal integrada.'),
            )
        if meta is None:
            meta = fallback_meta(col)

        label, source, stat_unit, unit, description = meta
        rows.append({
            'variable': col,
            'label_es': label,
            'source_layer': source,
            'statistical_unit': stat_unit,
            'territorial_level': 'comuna',
            'unit': unit,
            'denominator_or_weight': denominator(col),
            'description': description,
            'comparability_note': comparison_note(col),
        })

    out = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)

    source_counts = out['source_layer'].value_counts().to_dict()
    text = [
        '# Diccionario del maestro comunal integrado',
        '',
        f'El archivo documenta **{len(out)} variables** del maestro `chile_digital_inclusion_communes_2026_integrated.csv`.',
        '',
        'La tabla canónica y legible por máquinas está en `data/metadata/communal_master_dictionary.csv`.',
        '',
        '## Principios',
        '',
        '- una fila del maestro representa una comuna',
        '- los porcentajes censales se mantienen separados de métricas de desempeño y registros de red',
        '- Ookla se interpreta como desempeño observado donde existieron tests, no como cobertura probabilística',
        '- los registros 4G/5G SUBTEL representan entidades puntuales publicadas por operador, no torres físicas únicas ni porcentaje de cobertura',
        '- la dependencia móvil es una proxy operacional del proyecto y no una categoría oficial del Censo',
        '- no se publican ponderadores, scores ni el Índice de Vulnerabilidad Digital completo',
        '',
        '## Variables por capa',
        '',
    ]
    for source, count in source_counts.items():
        text.append(f'- {source}: {count}')
    text += [
        '',
        '## Uso',
        '',
        'Antes de construir rankings o modelos, revisar `statistical_unit`, `denominator_or_weight` y `comparability_note`. No deben mezclarse mecánicamente hogares censales, personas ponderadas de encuesta, tests de red y registros puntuales de infraestructura.',
        '',
        'Última revisión: 2026-08-14.',
    ]
    OUT_MD.write_text('\n'.join(text) + '\n', encoding='utf-8')
    print(f'Wrote {len(out)} dictionary rows')


if __name__ == '__main__':
    main()
