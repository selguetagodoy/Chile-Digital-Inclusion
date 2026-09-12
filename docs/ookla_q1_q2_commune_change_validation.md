# Ookla Q1→Q2 2026: cambio comunal con referencia descriptiva de volumen

## Objetivo

Comparar el desempeño comunal observado por Ookla entre 2026Q1 y 2026Q2 evitando que cambios extremos con muy pocos tests se interpreten del mismo modo que cambios respaldados por un volumen mayor de observaciones.

## Unidad y métrica

La unidad analítica es `comuna × tipo de red` (`fixed` o `mobile`). La métrica de cambio principal es la variación porcentual de `download_mbps_test_weighted` entre Q1 y Q2. Los promedios de velocidad provienen de tiles Ookla ponderados por número de tests del tile.

## Referencia de tests

Para cada comuna y red se calcula:

`mean_tests_q1_q2 = (tests_Q1 + tests_Q2) / 2`

Luego, de forma separada para red fija y móvil, se calcula la media nacional de `mean_tests_q1_q2` entre las comunas comparables. Esa media se usa exclusivamente como referencia descriptiva de volumen.

Resultados del corte 2026Q1→2026Q2:

- Fijo: 341 comunas comparables; referencia = 1,545.807918 tests medios Q1-Q2; 83 comunas quedan en o sobre la referencia (24.340176%).
- Móvil: 341 comunas comparables; referencia = 357.533724 tests medios Q1-Q2; 99 comunas quedan en o sobre la referencia (29.032258%).

## Interpretación

`above_mean_tests_reference = True` significa que la comuna-red tiene un volumen medio de tests Q1-Q2 igual o superior a la media observada entre comunas comparables de esa red. No significa representatividad estadística, muestra probabilística ni validación poblacional.

El ranking `rank_change_desc_validated` / `rank_change_asc_validated` se calcula únicamente dentro de este subconjunto para facilitar una lectura robusta por volumen relativo. Todas las observaciones originales se conservan en el archivo de detalle.

## Productos

- `data/ookla/territorial/chile_2026q1_vs_2026q2_change_validation.csv`
- `data/ookla/territorial/chile_2026q1_vs_2026q2_test_reference.csv`
- `scripts/build_ookla_q1_q2_change_validation.py`

## Regla de evidencia

No se imputan tests, velocidades ni cambios. No se extrapolan valores entre trimestres. La referencia de volumen es un cálculo descriptivo derivado exclusivamente de observaciones Q1 y Q2 existentes.
