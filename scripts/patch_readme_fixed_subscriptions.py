#!/usr/bin/env python3
from pathlib import Path
p=Path('README.md')
s=p.read_text(encoding='utf-8')
s=s.replace('presencia de capas públicas RedAcceso y Aulas Conectadas 2025 territorializado por RBD. Conserva las **346 comunas y contiene 84 variables**.', 'presencia de capas públicas RedAcceso, Aulas Conectadas 2025 territorializado por RBD y conexiones fijas administrativas SUBTEL a marzo de 2026. Conserva las **346 comunas y contiene 89 variables**.',1)
marker='### Infraestructura fija pública — SUBTEL RedAcceso\n'
section="""### Conexiones fijas por comuna — SUBTEL marzo 2026

`data/fixed_infrastructure_2026/` extrae directamente del workbook administrativo oficial las hojas `7.11.CO_FIJAS_COMUNA` y `7.11.1.CO_FIJAS_RES_COMUNA` para marzo de 2026.

La fuente reporta **342 de las 346 comunas** del catálogo territorial. Frutillar, Queilén, Purranque y Pedro Aguirre Cerda no aparecen reportadas en esas hojas para el corte utilizado y se mantienen como faltantes; no se imputan como cero. El control de nombres fuente no deja filas comunales sin resolver.

El maestro integrado incorpora conexiones fijas totales, conexiones residenciales, participación residencial y una razón de conexiones residenciales por 100 hogares del Censo 2024. Esta última es una intensidad administrativa descriptiva y **no debe interpretarse como porcentaje de cobertura de hogares**.

La trazabilidad está en `data/fixed_infrastructure_2026/extraction_manifest.csv` y la metodología en `data/fixed_infrastructure_2026/README.md`.

"""
if section.strip() not in s:
    if marker not in s: raise SystemExit('README insertion marker not found')
    s=s.replace(marker,section+marker,1)
p.write_text(s,encoding='utf-8')
print('README synchronized to 89-variable master')
