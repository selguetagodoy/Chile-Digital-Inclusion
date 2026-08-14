# Ookla Open Data — capa territorial Chile

Esta carpeta transforma los tiles oficiales de Ookla Open Data en agregados territoriales comparables para Chile.

## Productos

- `chile_2026q1_communes.csv` — Q1 2026 por comuna y tipo de red.
- `chile_2026q1_regions.csv` — Q1 2026 por región y tipo de red.
- `chile_2025q4_vs_2026q1_communes.csv` — comparación Q4 2025 → Q1 2026 por comuna.
- `chile_2025q4_vs_2026q1_regions.csv` — comparación trimestral por región.
- `spatial_assignment_coverage.csv` — control de asignación espacial de tiles y tests.

La salida Q1 2026 contiene 683 filas comuna × red y 32 filas región × red. El número de filas comunales no equivale a 346 × 2 porque la capa cartográfica BCN contiene 345 polígonos y, además, algunas combinaciones comuna × red no tienen tests asignados.

## Método

Cada tile se asigna mediante su centroide al polígono comunal BCN que lo contiene. Dentro de cada territorio, descarga, carga y latencias se calculan como promedio de las medias de tile ponderado por el número de tests de cada tile.

El proceso reconstruye Q4 2025 con la misma metodología antes de calcular variaciones hacia Q1 2026.

`spatial_assignment_coverage.csv` permite auditar qué proporción de tiles y tests quedó asociada a una comuna. La asignación de tests se mantiene en torno a 99% para las cuatro combinaciones período × red procesadas.

## Interpretación

Ookla representa desempeño observado donde existieron tests. No es una muestra probabilística de hogares ni una medida directa de cobertura comercial.

`devices_sum_across_tiles` es una suma de dispositivos reportados por tile. No debe interpretarse como número de usuarios o dispositivos únicos de una comuna.

Las métricas Ookla se mantienen separadas de las variables censales y de encuesta dentro del diccionario del maestro comunal.

## Reproducibilidad

`scripts/build_ookla_territorial.py` genera estos productos. El workflow `build-ookla-territorial.yml` reconstruye Q4 2025 desde los Parquet oficiales, procesa Q1 2026 y actualiza el maestro comunal integrado.

Última revisión: 2026-08-13.
