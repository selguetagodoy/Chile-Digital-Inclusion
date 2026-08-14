# Pipeline de bases oficiales SUBTEL

## Propósito

Esta capa procesa las bases públicas de las Encuestas de Acceso y Usos de Internet de SUBTEL para construir evidencia agregada, trazable y reproducible. El repositorio no redistribuye registros individuales.

## Cobertura procesada

Actualmente se han procesado bases oficiales correspondientes a 2008 y a las olas disponibles entre 2011 y 2025. El catálogo operativo está en `data/subtel_microdata/processed_base_catalog.csv`.

El barrido principal de las bases 2011–2025 inventaría 4.514 variables y publica 6.812 filas de distribuciones categóricas que cumplen la regla de tamaño mínimo de celda. La base 2008 agrega 309 variables y 862 distribuciones categóricas. La recuperación separada del archivo de personas 2011 agrega 21 variables y 69 distribuciones. En conjunto, la infraestructura actual inventaría 4.844 variables y 7.743 filas categóricas agregadas antes de la capa de ponderación.

## Archivos principales

### `data/subtel_microdata/`

- `dataset_manifest.csv` — bases procesadas, dimensiones y enlaces oficiales.
- `processed_base_catalog.csv` — catálogo consolidado de archivos y factores de expansión.
- `variable_dictionary.csv` — nombre, etiqueta, tipo, cobertura y etiquetas de valores de 4.514 variables del barrido 2011–2025.
- `categorical_distributions.csv` — distribuciones agregadas sin ponderar con supresión de celdas pequeñas.
- `numeric_summary.csv` — estadísticos descriptivos para variables numéricas de alta cardinalidad.
- `weight_candidates.csv` — variables potenciales de expansión detectadas durante la inspección.
- `harmonization_candidates.csv` — clasificación temática automática de variables.
- `harmonization_domain_coverage.csv` — cobertura de dominios por ola.
- `top_harmonization_candidates.csv` — candidatos prioritarios para construir el crosswalk entre cuestionarios.

### `data/subtel_weighted/`

Contiene las mismas distribuciones categóricas y resúmenes numéricos con dos universos de ponderación cuando la base lo permite.

- ponderación de hogar
- ponderación de persona

No debe elegirse un factor solo porque produzca una cifra plausible. La unidad estadística debe corresponder al universo de la pregunta.

### `data/subtel_2008/`

Perfil agregado de la base SPSS histórica disponible para 2008. El archivo RAR oficial se descarga durante la ejecución y se elimina al terminar.

### `data/subtel_2011_person/`

Recuperación del archivo de personas de 2011. La base usa una codificación heredada y requiere lectura `latin1`.

## Factores de expansión identificados

| Ola | Hogar | Persona |
|---|---|---|
| XII 2025 | `FE_HOGAR` | `FE_PERSONAS` |
| XI 2024 | `POND_HOGAR_FE` | `PON_PER_SIN_GSE_FE` |
| X 2023 | `FE_HOGAR` | `FE_USO` |
| IX 2017 | `FACTOR_HOGAR` | `FACTOR_PERSONA` |
| VIII 2016 | `FACT_HOGAR` | `FACT_PER` |
| VII 2015 | `factor_hogar_2016` | `FACT_PER` |
| VI | `FACTOR` | `FACTOR` |
| V | `fact_hog` | `fact_selec` |
| IV 2012 | no seleccionado | no seleccionado |
| III 2011 | `Factor_Transv` en base transversal | `Factor_Transv` en base transversal |

La ola IV se mantiene sin ponderador seleccionado mientras no exista evidencia suficiente para identificar un factor de expansión adecuado en la base disponible.

## Protección de la publicación

El pipeline aplica las siguientes reglas.

1. Los SAV, ZIP y RAR originales se descargan temporalmente durante GitHub Actions y no se incorporan al repositorio.
2. No se publican filas de personas u hogares.
3. No se publican respuestas abiertas ni campos detectados como texto libre.
4. Una categoría solo se publica cuando tiene al menos 30 casos sin ponderar.
5. Los ponderadores se conservan separados por universo de hogar y persona.
6. Los cambios de cuestionario se documentan y no se rellenan mediante interpolación.

## Armonización longitudinal

La clasificación automática no define por sí sola una serie comparable. Su función es reducir el universo de miles de preguntas a candidatos revisables en dominios como acceso, fijo/móvil, dispositivos, edad, sexo, ruralidad, ingresos/GSE, barreras, banca, Estado digital, trabajo, educación, seguridad y habilidades.

El archivo `top_harmonization_candidates.csv` sirve como punto de partida para validar manualmente equivalencias entre cuestionarios. Una variable se incorpora a una serie longitudinal solo cuando el concepto, el universo y las categorías son suficientemente comparables.

## Reproducibilidad

Los scripts principales son:

```text
scripts/profile_subtel_microdata.py
scripts/build_subtel_weighted_profiles.py
scripts/classify_subtel_variables.py
scripts/build_subtel_crosswalk.py
scripts/profile_subtel_2008.py
scripts/profile_subtel_2011_person.py
```

Los workflows asociados vuelven a descargar las fuentes oficiales y reconstruyen únicamente los productos agregados.

Última revisión: 2026-08-13.
