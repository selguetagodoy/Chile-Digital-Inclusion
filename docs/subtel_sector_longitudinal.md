# Serie administrativa SUBTEL — Internet fijo, móvil y tráfico

Esta capa normaliza las series administrativas oficiales de SUBTEL publicadas hasta junio de 2026. Su propósito es separar la evolución del mercado —conexiones, tecnologías y tráfico— de las encuestas de hogares y de las métricas de desempeño observadas por Ookla u OTI.

## Fuentes oficiales

El pipeline descarga cuatro libros XLSX desde la sección **Internet** de SUBTEL:

- conexiones de Internet fija;
- conexiones de Internet móvil;
- tráfico de datos móviles;
- tráfico de datos fijos.

Al 27 de agosto de 2026, SUBTEL publica las cuatro series con cierre en **junio de 2026**. Los archivos fuente utilizados por el pipeline están registrados en `data/subtel_sector_2026/source_catalog_2026q2.csv`.

El libro de conexiones fijas contiene observaciones desde diciembre de 2000. La hoja de conexiones móviles por tecnología comienza en diciembre de 2009; tráfico móvil en junio de 2017 y tráfico fijo en enero de 2019. El repositorio conserva el rango efectivo de cada hoja y no interpola períodos anteriores.

## Productos canónicos

`data/subtel_sector_series/` contiene:

- `fixed_connections_monthly.csv` — conexiones fijas totales y penetración por período;
- `mobile_connections_by_technology_monthly.csv` — 2G, 3G, 4G, 5G, total y penetraciones;
- `mobile_data_traffic_monthly.csv` — downlink, uplink y tráfico móvil total;
- `fixed_data_traffic_monthly.csv` — downlink, uplink y tráfico fijo total;
- `fixed_technology_snapshot_2026_06.csv` — composición tecnológica fija a junio de 2026 con etiquetas explícitas del libro SUBTEL;
- `sector_core_monthly_long.csv` — tabla longitudinal en formato largo para análisis y visualización;
- `sector_core_december_long_2000_2025.csv` — cortes de diciembre de años completos, sin interpolación;
- `series_qa.csv` — controles de rango, unicidad y reconciliación con publicaciones oficiales.

## Rango efectivo normalizado

El QA vigente registra:

| Serie | Primera observación | Última observación |
|---|---|---|
| Conexiones fijas | 2000-12 | 2026-06 |
| Conexiones móviles por tecnología | 2009-12 | 2026-06 |
| Tráfico móvil | 2017-06 | 2026-06 |
| Tráfico fijo | 2019-01 | 2026-06 |

La hoja de conexiones fijas contiene una tabla anual de cierres de diciembre y, desde 2010, una serie mensual que vuelve a incluir diciembre. El pipeline detectó ese solapamiento y conserva **una sola observación por período**, priorizando la fila mensual más específica cuando ambas existen. El control final deja 208 filas y 208 períodos únicos.

## Corte junio de 2026

La serie mensual oficial registra:

- conexiones fijas totales: **4.900.369**;
- conexiones móviles totales: **22.620.235**;
- conexiones móviles 3G+4G+5G: **22.590.623**;
- 4G: **11.446.039**;
- 5G: **10.818.497**.

El valor mensual exacto de 5G coincide con el snapshot sectorial del primer semestre de 2026.

## Tecnología fija

La hoja histórica nacional `7.7.CO_TEC_FIJAS` cambia de estructura y significado de columnas en el tiempo. Por esa razón no se publica como una serie tecnológica homogénea de largo plazo.

Para junio de 2026 se usa la hoja actual `7.7.1.CO_TEC_RG_EMP_FIJAS`, cuyos totales están etiquetados explícitamente. El corte normalizado registra:

- ADSL: **8.979** conexiones;
- HFC: **429.072**;
- WiMAX: **40**;
- FTTX/fibra: **4.275.932**;
- otras tecnologías fijas, calculadas como residual: **186.346**;
- total fijo: **4.900.369**.

FTTX/fibra representa **87,257%** del total, consistente con el **87,3%** publicado por SUBTEL para junio de 2026.

El residual `OTHER_FIXED_TECHNOLOGIES_RESIDUAL` se calcula como total fijo menos ADSL, HFC, WiMAX y FTTX explícitamente etiquetados. No se redistribuye entre tecnologías no identificadas.

## Revisión de vintages oficiales

Las planillas de junio pueden revisar observaciones previamente publicadas. Por ejemplo, el XLSX vigente registra **4.862.699 conexiones fijas en marzo de 2026**, mientras el snapshot sectorial Q1 conservado en otra capa había informado 4.859.679. El repositorio mantiene ambos valores con su procedencia correspondiente:

- para la serie longitudinal se usa el workbook mensual más reciente como vintage canónico;
- para snapshots históricos se conserva la cifra de la publicación específica correspondiente a ese corte.

Este criterio evita mezclar revisiones posteriores con cifras históricas sin documentarlo.

## Diferencia respecto de encuestas, OTI y Ookla

Esta capa utiliza registros administrativos de conexiones y tráfico.

- No equivale a hogares con acceso del Censo o de las encuestas SUBTEL.
- Una conexión móvil no equivale a una persona única.
- OTI mide velocidad fija bajo un sistema de medición regulatorio distinto.
- Ookla representa desempeño observado en tests Speedtest.
- Los registros 4G/5G ArcGIS representan entidades de red publicadas y no conexiones activas.

Estas capas pueden analizarse conjuntamente, pero sus denominadores y procesos de generación se mantienen separados.

## Reproducibilidad y QA

`scripts/build_subtel_sector_series_2026.py` descarga directamente los cuatro XLSX oficiales de junio de 2026, extrae hojas y columnas verificadas y exige que las cuatro series terminen en `2026-06`.

`scripts/qa_normalize_subtel_fixed_periods.py` elimina el solapamiento entre cierres anuales y filas mensuales de la serie fija, aplicando una regla reproducible de precedencia por fila fuente y verificando unicidad temporal.

Los controles vigentes confirman, entre otros:

- 208 períodos únicos de conexiones fijas;
- 199 períodos únicos de conexiones móviles;
- 109 períodos únicos de tráfico móvil;
- 90 períodos únicos de tráfico fijo;
- 4.900.369 conexiones fijas a junio de 2026;
- 4.275.932 conexiones FTTX/fibra;
- 11.446.039 conexiones 4G;
- 10.818.497 conexiones 5G;
- reconciliación exacta del snapshot tecnológico fijo con el total nacional.

Última revisión: 2026-08-27.
