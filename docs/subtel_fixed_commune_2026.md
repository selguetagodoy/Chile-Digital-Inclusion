# Conexiones fijas por comuna — SUBTEL marzo 2026

## Propósito

Esta nota documenta la reconstrucción comunal de conexiones de Internet fija de marzo de 2026 utilizada por `Chile-Digital-Inclusion`.

La capa se construye desde el workbook oficial de SUBTEL `Series conexiones Internet fija`, utilizando:

- `7.11.CO_FIJAS_COMUNA` para conexiones fijas totales;
- `7.11.1.CO_FIJAS_RES_COMUNA` para conexiones fijas residenciales.

El archivo original se descarga durante la ejecución y no se republica en el repositorio.

## Problema detectado en la fuente

La auditoría del workbook mostró que, en la columna de marzo de 2026, algunas filas que conservan una etiqueta de comuna contienen en realidad fórmulas de subtotal regional. La desalineación aparece en la zona de la hoja afectada por la separación territorial Biobío–Ñuble y continúa en filas posteriores.

Por esa razón no es válido asumir que la etiqueta de la columna de comuna y el valor de marzo de 2026 pertenecen siempre a la misma observación.

El error era material. Una extracción por nombre podía asignar, por ejemplo, subtotales regionales a comunas individuales. La reconstrucción actual elimina esa posibilidad.

## Método de reconstrucción

El pipeline `scripts/build_subtel_fixed_commune_2026.py` aplica el siguiente procedimiento por separado a total y residencial.

1. Localiza dinámicamente la columna correspondiente a marzo de 2026 a partir de las cabeceras de año y mes.
2. Carga el workbook dos veces, una con valores cacheados y otra con fórmulas visibles.
3. Identifica las 16 fórmulas de subtotal regional de la columna objetivo.
4. Usa el rango de cada fórmula para delimitar el bloque de posiciones comunales de esa región.
5. Ordena el catálogo actual de comunas según la nomenclatura utilizada por la fuente. Se conserva, por ejemplo, la posición histórica de `Calera` para la actual comuna del catálogo con ese nombre fuente.
6. Cuando el bloque contiene una fila auxiliar adicional, conserva únicamente las posiciones numéricas necesarias para el número actual de comunas de la región.
7. Cuando el bloque contiene exactamente una posición por comuna, conserva también las celdas vacías en su posición original; no las transforma en cero.
8. Asigna las posiciones a las comunas actuales en el orden de la fuente.
9. Exige que el número de posiciones mapeadas sea igual al número de comunas del catálogo regional.
10. Exige que la suma de los valores mapeados sea idéntica al subtotal regional del workbook.

Las regiones 1 a 7, cuya zona de etiquetas permanece alineada, se utilizan además como control independiente del orden: la secuencia mapeada debe coincidir completamente con las etiquetas de la fuente.

## Controles publicados

`data/fixed_infrastructure_2026/source_alignment_qa.csv` contiene 32 controles, equivalentes a 16 regiones por dos métricas.

Un release válido requiere simultáneamente:

- `count_status=pass`;
- `subtotal_status=pass`;
- `subtotal_delta=0`;
- `label_order_status=pass`.

`data/fixed_infrastructure_2026/source_row_mapping_2026_03.csv` publica 692 mapeos fila fuente → comuna, correspondientes a 346 posiciones para total y 346 para residencial.

`data/subtel_sector_series/fixed_commune_source_rows_2026_03.csv` conserva además la fila original, la etiqueta visible, el valor de marzo de 2026 y la fórmula cuando existe.

La validación `scripts/validate_fixed_commune_reconstruction.py` comprueba la reconstrucción completa y exige igualdad entre la capa fuente reconstruida y los campos incorporados al maestro comunal.

## Cobertura resultante

La reconstrucción obtiene valores numéricos para 345 de las 346 comunas del catálogo.

La única excepción es Antártica, código 12202. Su posición está presente en el bloque regional de Magallanes, pero la celda de marzo de 2026 está explícitamente vacía tanto en conexiones totales como residenciales. La observación se conserva como `source_blank` y no se imputa como cero.

## Ejemplos de correcciones verificadas

La reconstrucción actual asigna, entre otros:

| Comuna | Código | Conexiones fijas totales | Residenciales |
|---|---:|---:|---:|
| Cabrero | 8303 | 5.656 | 5.525 |
| Cañete | 8203 | 5.476 | 5.336 |
| Lautaro | 9108 | 8.129 | 7.869 |
| Frutillar | 10105 | 4.904 | 4.737 |
| Queilén | 10207 | 500 | 463 |
| Purranque | 10303 | 3.482 | 3.362 |
| Futaleufú | 10402 | 868 | 816 |
| Pedro Aguirre Cerda | 13121 | 23.818 | 23.143 |
| Portezuelo | 16205 | 326 | 314 |

Estos valores no se fijan manualmente en la capa. La tabla es únicamente un conjunto de casos de control derivado del mismo procedimiento reproducible.

## Interpretación

Los campos son conteos administrativos de conexiones, no hogares únicos ni porcentaje de cobertura territorial.

La razón `subtel_fixed_residential_per_100_censo_households_2026m03` divide conexiones residenciales de marzo de 2026 por hogares del Censo 2024. Es una medida descriptiva de intensidad y puede superar 100; no debe presentarse como tasa de cobertura de hogares.

Última revisión: 2026-08-15.
