# Infraestructura y conexiones fijas — SUBTEL marzo 2026

Esta carpeta transforma la serie administrativa oficial de Internet fija de SUBTEL en una capa comunal reproducible.

## Fuente

Workbook oficial `Series conexiones Internet fija`, actualizado a marzo de 2026. El pipeline descarga temporalmente el XLSX desde SUBTEL y no almacena el archivo original en GitHub.

Se utilizan dos hojas del libro:

- `7.11.CO_FIJAS_COMUNA` — conexiones fijas totales por comuna
- `7.11.1.CO_FIJAS_RES_COMUNA` — conexiones fijas residenciales por comuna

## Producto principal

`commune_fixed_connections_2026_03.csv` contiene las 346 comunas del catálogo territorial del proyecto. La fuente reporta valores para 342 de ellas. Los cuatro casos sin fila comunal reportada se conservan como faltantes y `source_status=source_not_reported`; no se imputan como cero.

`source_not_reported_communes.csv` identifica esos casos. `source_match_qa.csv` debe contener solamente el encabezado cuando todos los nombres presentes en la fuente fueron resueltos.

## Integración

El maestro comunal agrega:

- conexiones fijas totales
- conexiones fijas residenciales
- participación residencial dentro de conexiones fijas
- conexiones residenciales fijas por 100 hogares del Censo 2024
- estado de reporte de la fuente

El indicador por 100 hogares es una **razón administrativa descriptiva**, no una tasa de cobertura. Una conexión no equivale necesariamente a un hogar único y los períodos/denominadores de SUBTEL y Censo no son idénticos.

Última revisión: 2026-08-14.
