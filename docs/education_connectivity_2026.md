# Conectividad educativa — Chile 2026

Esta capa registra programas públicos de infraestructura y conectividad digital educativa sin convertirlos automáticamente en una medida de acceso efectivo de los estudiantes.

## Fuentes incorporadas

`data/education_connectivity_2026/program_catalog.csv` resume programas y parámetros publicados por el Ministerio de Educación:

- **Conectividad para la Educación 2030 (CpE2030)** — continuidad y consolidación del programa con horizonte 2029.
- **CpE2030 2025/2026** — estándar obligatorio informado para 2025 de 500 kbps por estudiante y documentación de selección 2026.
- **Aulas Conectadas 2025** — 700 establecimientos beneficiarios, 23 SLEP y 127 sostenedores/entidades adicionales informados por Mineduc.
- **Conectividad para la Educación** — servicio histórico iniciado en 2011 con continuidad informada hasta 2026.
- **Prendo y Aprendo** — solución para escuelas rurales aisladas de hasta cinco estudiantes fuera de CpE2030, basada en contenidos precargados; no equivale a acceso continuo a Internet.

## Aulas Conectadas 2025 — nómina oficial con RBD

Mineduc publica una hoja de cálculo específica denominada **Nómina de establecimientos seleccionados y lista de espera Aulas Conectadas 2025**.

El pipeline descarga directamente esa hoja pública y normaliza únicamente campos institucionales:

- RBD
- nombre del establecimiento
- región
- nombre del sostenedor
- proyecto
- estado de selección
- posición en lista de espera cuando corresponde

`aulas_conectadas_2025_establishments.csv` contiene **793 RBD únicos**: 700 seleccionados y 93 en lista de espera. `aulas_conectadas_2025_sheet_qa.csv` verifica ambos conteos y la unicidad de la llave RBD.

`aulas_conectadas_2025_region_summary.csv` entrega un resumen por región y grupo de selección.

La planilla oficial no incluye comuna. Esa dimensión se incorporará únicamente mediante un crosswalk RBD → directorio oficial de establecimientos Mineduc; no se inferirá a partir del nombre del colegio o del sostenedor.

## Resoluciones escaneadas

El repositorio también audita las resoluciones vinculadas por Mineduc:

- REX N°497 de 2026 de CpE2030
- REX N°775 de 2025 de la convocatoria que incluye Aulas Conectadas

Ambos PDF públicos se descargan correctamente, pero no contienen capa de texto ni tablas extraíbles en las pruebas automáticas. No se usa OCR para construir la nómina cuando existe una fuente administrativa estructurada mejor.

Archivos de auditoría:

- `cpe2030_2026_rex497_extraction_summary.csv`
- `cpe2030_2026_rex497_text_audit.csv`
- `cpe2030_2026_rex497_rbd_candidates.csv`
- `aulas_conectadas_2025_rex775_extraction_summary.csv`
- `aulas_conectadas_2025_rex775_rbd_candidates.csv`

## Próxima integración territorial

La siguiente llave es el Directorio oficial de Establecimientos Educacionales 2025 del Centro de Estudios Mineduc. Permitirá resolver, cuando esté disponible en formato reutilizable:

`RBD → comuna → región → ruralidad → dependencia → SLEP`.

Con ello se podrá agregar Aulas Conectadas por comuna y cruzarlo descriptivamente con conectividad de hogares, infraestructura pública y desempeño de red, manteniendo separados los universos estadísticos.

## Reglas de interpretación

- `beneficiary_establishments` es un conteo administrativo de un programa, no una tasa de conectividad escolar.
- `bandwidth_standard_per_student` es un estándar contractual/programático, no velocidad efectivamente medida.
- estar seleccionado en Aulas Conectadas acredita participación administrativa en el programa, no que la red interna ya esté completamente habilitada.
- pertenecer a un programa no demuestra que todos los hogares de sus estudiantes tengan Internet.
- la capa educativa debe mantenerse separada de Censo, CASEN, SUBTEL hogares y Ookla por sus diferentes unidades estadísticas.

Fuentes oficiales registradas en `program_catalog.csv` y en los propios archivos normalizados.

Última revisión: 2026-08-14.
