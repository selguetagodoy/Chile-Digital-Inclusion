# Conectividad educativa — Chile 2026

Esta capa registra programas públicos de infraestructura y conectividad digital educativa sin convertirlos automáticamente en una medida de acceso efectivo de los estudiantes.

## Fuentes incorporadas

`data/education_connectivity_2026/program_catalog.csv` resume programas y parámetros publicados por el Ministerio de Educación:

- **Conectividad para la Educación 2030 (CpE2030)** — continuidad y consolidación del programa con horizonte 2029.
- **CpE2030 2025/2026** — estándar obligatorio informado para 2025 de 500 kbps por estudiante y documentación de selección 2026.
- **Aulas Conectadas 2025** — 700 establecimientos seleccionados; la fuente programática también reporta 23 SLEP y 127 sostenedores/entidades adicionales.
- **Conectividad para la Educación** — servicio histórico iniciado en 2011 con continuidad informada hasta 2026.
- **Prendo y Aprendo** — solución para escuelas rurales aisladas de hasta cinco estudiantes fuera de CpE2030, basada en contenidos precargados; no equivale a acceso continuo a Internet.

## Aulas Conectadas 2025 — nómina oficial con RBD

Mineduc publica una hoja de cálculo denominada **Nómina de establecimientos seleccionados y lista de espera Aulas Conectadas 2025**. El pipeline descarga directamente esa fuente y normaliza únicamente campos institucionales.

`aulas_conectadas_2025_establishments.csv` contiene **793 RBD únicos**:

- 700 seleccionados
- 93 en lista de espera

`aulas_conectadas_2025_sheet_qa.csv` verifica los conteos y la unicidad de la llave RBD.

## Directorio oficial de Establecimientos Educacionales 2025

Para territorializar los RBD, el repositorio descarga el archivo oficial `Directorio-Oficial-EE-2025.rar` del portal Datos Abiertos Mineduc. El archivo contiene un CSV con **16.768 establecimientos y 58 variables** de datos, además del encabezado.

Entre las variables utilizadas están:

- `RBD`
- `NOM_RBD`
- `COD_REG_RBD` y `NOM_REG_RBD_A`
- `COD_COM_RBD` y `NOM_COM_RBD`
- `RURAL_RBD`
- `LATITUD` y `LONGITUD`
- dependencia administrativa
- `MAT_TOTAL`
- estado del establecimiento

No se publican RUT del sostenedor ni otros identificadores administrativos innecesarios para esta capa.

## Crosswalk RBD → comuna

`build_mineduc_aulas_communal_2025.py` cruza las dos fuentes usando exclusivamente RBD. El QA registra:

- 793 RBD del programa
- 793 RBD únicos
- 16.768 RBD únicos en el Directorio oficial
- cero duplicados de RBD en el Directorio
- **793 de 793 RBD emparejados**
- **100% de match**
- cero establecimientos sin resolver

La capa comunal resultante tiene las 346 comunas. Los 700 seleccionados se distribuyen en **196 comunas** y los 93 registros de lista de espera también quedan territorializados.

Productos principales:

- `aulas_conectadas_2025_establishments.csv` — fuente normalizada del programa
- `aulas_conectadas_2025_establishments_enriched.csv` — RBD enriquecido con territorio, ruralidad, coordenadas y matrícula del Directorio oficial
- `aulas_conectadas_2025_commune_summary.csv` — resumen para las 346 comunas
- `aulas_conectadas_2025_crosswalk_qa.csv` — control de completitud del cruce
- `aulas_conectadas_2025_region_summary.csv` — resumen regional

El resumen comunal incluye número de establecimientos seleccionados, lista de espera, seleccionados rurales, suma de matrícula de establecimientos seleccionados y número de seleccionados con coordenadas disponibles.

La suma de `MAT_TOTAL` describe el tamaño administrativo de los establecimientos seleccionados. **No debe interpretarse como número de estudiantes efectivamente beneficiados por una intervención ya ejecutada.**

## Resoluciones escaneadas

El repositorio también audita las resoluciones vinculadas por Mineduc:

- REX N°497 de 2026 de CpE2030
- REX N°775 de 2025 de la convocatoria que incluye Aulas Conectadas

Ambos PDF públicos se descargan correctamente, pero no contienen capa de texto ni tablas extraíbles en las pruebas automáticas. No se usa OCR para construir la nómina porque existen fuentes administrativas estructuradas y más confiables.

Archivos de auditoría:

- `cpe2030_2026_rex497_extraction_summary.csv`
- `cpe2030_2026_rex497_text_audit.csv`
- `cpe2030_2026_rex497_rbd_candidates.csv`
- `aulas_conectadas_2025_rex775_extraction_summary.csv`
- `aulas_conectadas_2025_rex775_rbd_candidates.csv`

## Reglas de interpretación

- `selected_establishments` es un conteo administrativo de establecimientos seleccionados, no una tasa de conectividad escolar.
- `bandwidth_standard_per_student` es un estándar contractual/programático, no velocidad efectivamente medida.
- estar seleccionado en Aulas Conectadas acredita participación administrativa en el programa, no que la red interna ya esté completamente habilitada.
- pertenecer a un programa no demuestra que todos los hogares de sus estudiantes tengan Internet.
- la capa educativa se mantiene separada de Censo, CASEN, SUBTEL hogares y Ookla por sus diferentes unidades estadísticas.

Última revisión: 2026-08-14.
