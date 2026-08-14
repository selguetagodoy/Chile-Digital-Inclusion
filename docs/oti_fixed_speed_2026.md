# OTI — velocidad de Internet fijo por región, enero 2026

Esta capa incorpora los promedios regionales publicados por SUBTEL a partir de las mediciones del Organismo Técnico Independiente (OTI) para conexiones de Internet fija.

El archivo principal es:

`data/oti_2026/regional_fixed_speed_2026_01.csv`

## Corte disponible

La publicación oficial del 3 de febrero de 2026 informa **752.626 mediciones** realizadas durante enero de 2026 en distintas zonas del país y entrega velocidad promedio de bajada y subida para las 16 regiones.

Los mayores promedios de bajada publicados para ese mes corresponden a Los Lagos, Ñuble y Biobío. La tabla completa se conserva en el CSV, sin convertirla en un ranking compuesto.

## Diferencia respecto de Ookla

OTI y Ookla se mantienen como capas distintas.

- OTI forma parte del marco chileno de medición asociado a la Ley de Velocidad Mínima Garantizada y SUBTEL publica sus resultados regionales.
- Ookla Open Data representa agregados de tests Speedtest en tiles y utiliza otra fuente, metodología y proceso de agregación.
- Ninguna de las dos capas equivale a porcentaje de hogares con acceso ni a cobertura geográfica universal.
- No deben compararse valores OTI y Ookla como si provinieran del mismo instrumento.

## Unidad territorial

La capa OTI se mantiene a nivel **regional**. No se replica el promedio regional en las 346 filas del maestro comunal porque eso agregaría columnas redundantes y podría inducir una falsa precisión comunal.

## Trazabilidad

El CSV registra:

- período de medición;
- código y nombre de región;
- Mbps de bajada;
- Mbps de subida;
- número nacional de mediciones informado por SUBTEL;
- fecha de publicación;
- URL de la publicación oficial;
- advertencia metodológica.

La página oficial muestra una inconsistencia editorial en su dateline interno —menciona 2025—, mientras el encabezado, la fecha de publicación y el cuerpo identifican enero/febrero de 2026. El dataset utiliza `publication_date=2026-02-03` y `period=2026-01` de acuerdo con esos elementos concordantes.

Última revisión: 2026-08-14.
