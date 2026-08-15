#!/usr/bin/env python3
from pathlib import Path

p = Path('README.md')
s = p.read_text(encoding='utf-8')

s = s.replace(
    'presencia de capas públicas RedAcceso y Aulas Conectadas 2025 territorializado por RBD. Conserva las **346 comunas y contiene 84 variables**.',
    'presencia de capas públicas RedAcceso, Aulas Conectadas 2025 territorializado por RBD y conexiones fijas administrativas SUBTEL a marzo de 2026. Conserva las **346 comunas y contiene 89 variables**.',
    1,
)

start = '### Conexiones fijas por comuna — SUBTEL marzo 2026\n'
end = '### Infraestructura fija pública — SUBTEL RedAcceso\n'
section = """### Conexiones fijas por comuna — SUBTEL marzo 2026

`data/fixed_infrastructure_2026/` reconstruye el corte comunal de marzo de 2026 desde las hojas oficiales `7.11.CO_FIJAS_COMUNA` y `7.11.1.CO_FIJAS_RES_COMUNA`.

El workbook mantiene etiquetas comunales desalineadas en parte de la hoja después de la separación territorial Biobío–Ñuble. Por esa razón el pipeline **no empareja ciegamente nombre y celda**. Delimita los 16 bloques regionales mediante sus fórmulas de subtotal, ordena el catálogo comunal con la nomenclatura de la fuente y exige, para conexiones totales y residenciales, coincidencia en el número de comunas y conciliación exacta contra cada subtotal regional. Las 32 verificaciones regionales publicadas tienen delta cero.

El resultado recupera valores numéricos para **345 de 346 comunas**. La única excepción es Antártica (12202), cuya posición comunal está presente en el bloque regional pero la celda fuente está explícitamente vacía; se conserva como `source_blank` y **no se imputa como cero**.

El maestro integrado incorpora conexiones fijas totales, conexiones residenciales, participación residencial y una razón de conexiones residenciales por 100 hogares del Censo 2024. Esta última es una intensidad administrativa descriptiva y **no debe interpretarse como porcentaje de cobertura de hogares**.

La trazabilidad incluye `extraction_manifest.csv`, `source_alignment_qa.csv` y `source_row_mapping_2026_03.csv`. El audit de las filas originales se publica además en `data/subtel_sector_series/fixed_commune_source_rows_2026_03.csv`.

"""

if start in s and end in s:
    before, tail = s.split(start, 1)
    _, after = tail.split(end, 1)
    s = before + section + end + after
elif end in s:
    s = s.replace(end, section + end, 1)
else:
    raise SystemExit('README fixed-infrastructure insertion marker not found')

p.write_text(s, encoding='utf-8')
print('README synchronized to reconciled 345+1 SUBTEL commune contract')
