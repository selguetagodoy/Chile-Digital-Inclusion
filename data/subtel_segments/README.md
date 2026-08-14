# SUBTEL — acceso segmentado

Esta carpeta publica tabulados ponderados de acceso propio y pagado a Internet en el hogar para las olas 2015, 2016, 2017, 2023, 2024 y 2025.

## Productos

- `household_paid_access_by_segment_2015_2025.csv` — maestro largo de segmentos.
- `household_paid_access_by_region_2015_2025.csv` — acceso por región.
- `household_paid_access_by_urban_rural_2015_2025.csv` — acceso urbano/rural.
- `household_paid_access_by_socioeconomic_group_2015_2025.csv` — quintil/GSE cuando existe una categoría explícita y verificable.
- `segment_mapping_manifest.csv` — variables y ponderadores usados en cada ola, junto con control contra la cifra nacional publicada.

## Regla metodológica

Se usa exclusivamente el factor de expansión de hogares correspondiente a cada encuesta. Las celdas con menos de 30 observaciones sin ponderar no se publican. El nivel socioeconómico no se reconstruye a partir de ingresos: entra solo si la base contiene una variable explícita de quintil o GSE con hasta diez categorías.

Las categorías se mantienen tal como vienen etiquetadas en cada ola. Esto permite análisis por año, pero no implica que las categorías socioeconómicas sean idénticas entre encuestas.

Los SAV oficiales se descargan durante GitHub Actions y no se almacenan en el repositorio.

Última revisión: 2026-08-13.
