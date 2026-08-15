# Infraestructura y conexiones fijas — SUBTEL marzo 2026

Esta carpeta transforma la serie administrativa oficial de Internet fija de SUBTEL en una capa comunal reproducible.

## Fuente

Workbook oficial `Series conexiones Internet fija`, actualizado a marzo de 2026. El pipeline descarga temporalmente el XLSX desde SUBTEL y no almacena el archivo original en GitHub.

Se utilizan dos hojas del libro:

- `7.11.CO_FIJAS_COMUNA` — conexiones fijas totales por comuna
- `7.11.1.CO_FIJAS_RES_COMUNA` — conexiones fijas residenciales por comuna

## Particularidad de la fuente

Las etiquetas de comuna de estas hojas quedan desalineadas en parte del libro después de la separación territorial Biobío–Ñuble. Por ello no es metodológicamente seguro asociar el valor de marzo de 2026 a la etiqueta que aparece en la misma fila.

El pipeline utiliza una reconstrucción determinística basada en la estructura del propio workbook:

1. localiza dinámicamente la columna de marzo de 2026;
2. identifica los 16 bloques regionales mediante las fórmulas de subtotal de la fuente;
3. ordena las comunas actuales siguiendo la nomenclatura usada por el workbook;
4. mapea cada posición del bloque regional a una comuna actual;
5. exige que el número de posiciones comunales coincida con el catálogo regional;
6. exige que la suma de los valores mapeados coincida exactamente con el subtotal regional;
7. repite el control de forma independiente para conexiones totales y residenciales.

`source_alignment_qa.csv` publica las 32 conciliaciones región × métrica. Todas deben presentar `count_status=pass`, `subtotal_status=pass` y `subtotal_delta=0`.

`source_row_mapping_2026_03.csv` conserva la trazabilidad desde cada fila del workbook hacia la comuna actual. El audit de la fila original, incluida su etiqueta y condición de fórmula, se encuentra además en `data/subtel_sector_series/fixed_commune_source_rows_2026_03.csv`.

## Producto principal

`commune_fixed_connections_2026_03.csv` contiene las 346 comunas del catálogo territorial del proyecto. La reconstrucción obtiene valores numéricos de conexiones totales y residenciales para **345 comunas**.

La única excepción es **Antártica (12202)**. Su posición existe dentro del bloque regional de Magallanes, pero la celda fuente de marzo de 2026 está explícitamente vacía tanto en total como en residencial. Se conserva como `source_status=source_blank` y no se imputa como cero.

Por compatibilidad histórica, `source_not_reported_communes.csv` conserva su nombre de archivo, pero actualmente contiene esa única observación `source_blank`.

`source_match_qa.csv` debe contener solamente el encabezado cuando no existen fallas de conciliación regional.

## Integración

El maestro comunal agrega:

- conexiones fijas totales
- conexiones fijas residenciales
- participación residencial dentro de conexiones fijas
- conexiones residenciales fijas por 100 hogares del Censo 2024
- estado de reporte de la fuente

El indicador por 100 hogares es una **razón administrativa descriptiva**, no una tasa de cobertura. Una conexión no equivale necesariamente a un hogar único y los períodos/denominadores de SUBTEL y Censo no son idénticos.

Última revisión: 2026-08-15.
