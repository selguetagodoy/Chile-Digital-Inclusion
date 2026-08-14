# Conectividad educativa — Chile 2026

Esta capa registra programas públicos de infraestructura y conectividad digital educativa sin convertirlos automáticamente en una medida de acceso efectivo de los estudiantes.

## Fuentes incorporadas

`data/education_connectivity_2026/program_catalog.csv` resume programas y parámetros publicados por el Ministerio de Educación:

- **Conectividad para la Educación 2030 (CpE2030)** — continuidad y consolidación del programa con horizonte 2029.
- **CpE2030 2025/2026** — estándar obligatorio informado para 2025 de 500 kbps por estudiante y documentación de selección 2026.
- **Aulas Conectadas 2025** — 700 establecimientos beneficiarios, 23 SLEP y 127 sostenedores/entidades adicionales informados por Mineduc.
- **Conectividad para la Educación** — servicio histórico iniciado en 2011 con continuidad informada hasta 2026.
- **Prendo y Aprendo** — solución para escuelas rurales aisladas de hasta cinco estudiantes fuera de CpE2030, basada en contenidos precargados; no equivale a acceso continuo a Internet.

## Resolución Exenta N°497 de 2026

El pipeline `scripts/extract_mineduc_cpe2030_2026.py` descarga la resolución pública vinculada por Mineduc y audita su legibilidad automática.

La primera extracción detectó un PDF válido de seis páginas pero ninguna tabla estructurada. El pipeline fue ampliado para comprobar también la capa de texto sin usar OCR. Los archivos de auditoría son:

- `cpe2030_2026_rex497_extraction_summary.csv`
- `cpe2030_2026_rex497_text_audit.csv`
- `cpe2030_2026_rex497_rbd_candidates.csv`

Un número extraído se considera solo **candidato RBD** y no un establecimiento confirmado hasta contrastarlo con un directorio oficial de establecimientos.

## Próxima integración territorial

Para incorporar establecimientos al maestro comunal se requieren dos elementos verificables:

1. una nómina oficial con RBD de los establecimientos seleccionados o beneficiarios;
2. un directorio oficial de establecimientos que permita resolver RBD → comuna, región, ruralidad, dependencia y SLEP.

La integración no se realizará desde nombres aproximados ni geocodificación heurística si existe una llave RBD oficial.

## Reglas de interpretación

- `beneficiary_establishments` es un conteo administrativo de un programa, no una tasa de conectividad escolar.
- `bandwidth_standard_per_student` es un estándar contractual/programático, no velocidad efectivamente medida.
- pertenecer a un programa no demuestra que todos los hogares de sus estudiantes tengan Internet.
- la capa educativa debe mantenerse separada de Censo, CASEN, SUBTEL hogares y Ookla por sus diferentes unidades estadísticas.

Fuentes oficiales registradas en `program_catalog.csv`.

Última revisión: 2026-08-14.
