# Serie administrativa SUBTEL — Internet fijo, móvil y tráfico

Esta capa normaliza las series administrativas oficiales de SUBTEL publicadas hasta marzo de 2026. Su propósito es separar la evolución del mercado —conexiones, tecnologías y tráfico— de las encuestas de hogares y de las métricas de desempeño observadas por Ookla u OTI.

## Fuentes oficiales

El pipeline descarga cuatro libros XLSX desde la sección **Internet** de SUBTEL:

- conexiones de Internet fija;
- conexiones de Internet móvil;
- tráfico de datos móviles;
- tráfico de datos fijos.

La página de SUBTEL presenta las series con estos rangos públicos:

- Internet fija: Q1 2002 → marzo 2026;
- Internet móvil: Q1 2002 → marzo 2026;
- tráfico móvil: junio 2017 → marzo 2026;
- tráfico fijo: enero 2019 → marzo 2026.

El libro de conexiones fijas contiene además observaciones desde diciembre de 2000. El repositorio conserva el rango efectivo disponible en el XLSX y documenta la diferencia respecto del rango anunciado en la página, sin eliminar observaciones válidas de la fuente.

## Productos canónicos

`data/subtel_sector_series/` contiene:

- `fixed_connections_monthly.csv` — conexiones fijas totales y penetración mensual;
- `mobile_connections_by_technology_monthly.csv` — 2G, 3G, 4G, 5G, total y penetraciones;
- `mobile_data_traffic_monthly.csv` — downlink, uplink y tráfico móvil total;
- `fixed_data_traffic_monthly.csv` — downlink, uplink y tráfico fijo total;
- `fixed_technology_snapshot_2026_03.csv` — composición tecnológica fija actual con etiquetas explícitas del libro SUBTEL;
- `sector_core_monthly_long.csv` — tabla longitudinal en formato largo para análisis y visualización;
- `sector_core_december_long_2000_2025.csv` — cortes de diciembre de años completos, sin interpolación;
- `series_qa.csv` — controles de rango, unicidad y reconciliación con publicaciones oficiales.

## Rango efectivo normalizado

El último QA registra:

| Serie | Primera observación del XLSX | Última observación |
|---|---|---|
| Conexiones fijas | 2000-12 | 2026-03 |
| Conexiones móviles por tecnología | 2009-12 | 2026-03 |
| Tráfico móvil | 2017-06 | 2026-03 |
| Tráfico fijo | 2019-01 | 2026-03 |

Las diferencias de fecha inicial reflejan la estructura efectiva de las hojas seleccionadas. No se completan años previos con interpolación ni con otras fuentes incompatibles.

## Tecnología fija

La hoja histórica nacional `7.7.CO_TEC_FIJAS` cambia de estructura y significado de columnas en las observaciones recientes. Por esa razón **no se publica como una serie tecnológica homogénea de largo plazo**.

Para marzo de 2026 se usa la hoja actual `7.7.1.CO_TEC_RG_EMP_FIJAS`, cuyos totales están etiquetados explícitamente. El corte normalizado registra:

- ADSL: 9.367 conexiones;
- HFC: 516.751;
- WiMAX: 68;
- FTTX/fibra: 4.147.629;
- otras tecnologías fijas, calculadas como residual del total: 185.864;
- total fijo: 4.859.679.

FTTX/fibra representa **85,35%** del total de marzo de 2026, coherente con el 85,3% informado por SUBTEL al cierre del trimestre.

El residual `OTHER_FIXED_TECHNOLOGIES_RESIDUAL` se calcula como total fijo menos ADSL, HFC, WiMAX y FTTX explícitamente etiquetados. No se redistribuye entre tecnologías no identificadas.

## 5G — discrepancia entre dos publicaciones oficiales

El libro mensual de conexiones móviles y otras publicaciones oficiales de SUBTEL no son perfectamente idénticos para el cierre de Q1 2026.

El XLSX mensual registra:

- enero 2026: **10.161.957** conexiones 5G;
- febrero 2026: 10.203.946;
- marzo 2026: **10.356.448**.

El valor de enero coincide exactamente con la publicación oficial de SUBTEL del 13 de abril de 2026 que informa 10.161.957 conexiones 5G a enero.

Por separado, el snapshot sectorial Q1 ya incorporado al repositorio conserva **10.367.754** conexiones 5G. La diferencia frente al XLSX mensual de marzo es de 11.306 conexiones, aproximadamente 0,11%.

El repositorio **no fuerza una reconciliación artificial**. Cada valor mantiene su fuente y su rol:

- la serie longitudinal mensual usa el XLSX oficial mensual;
- el snapshot sectorial mantiene la cifra de su publicación específica.

`series_qa.csv` deja visible esta diferencia como control de procedencia, no como fallo del pipeline.

## Diferencia respecto de encuestas, OTI y Ookla

Esta capa utiliza registros administrativos de conexiones y tráfico.

- No equivale a hogares con acceso del Censo o de las encuestas SUBTEL.
- Una conexión móvil no equivale a una persona única.
- OTI mide velocidad fija bajo un sistema de medición regulatorio distinto.
- Ookla representa desempeño observado en tests Speedtest.
- Los registros 4G/5G ArcGIS representan entidades de red publicadas y no conexiones activas.

Estas capas pueden analizarse conjuntamente, pero sus denominadores y procesos de generación deben mantenerse separados.

## Reproducibilidad

`scripts/build_subtel_sector_series_2026.py` descarga directamente los cuatro XLSX, extrae únicamente hojas y columnas verificadas y aplica controles obligatorios antes de permitir el commit.

Los controles actuales exigen, entre otros:

- que las cuatro series canónicas terminen en marzo de 2026;
- que las conexiones fijas de marzo sumen 4.859.679;
- que el snapshot tecnológico fijo reconcilie con ese mismo total;
- que FTTX sea 4.147.629;
- que enero 2026 registre 10.161.957 conexiones 5G;
- que marzo del XLSX mensual registre 10.356.448 conexiones 5G.

Las hojas de auditoría y perfil permanecen en la carpeta para hacer visibles los cambios de estructura detectados durante el procesamiento.

Última revisión: 2026-08-14.
