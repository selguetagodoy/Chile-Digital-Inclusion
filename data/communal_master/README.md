# Chile Digital Inclusion — maestro comunal público

Esta carpeta contiene dos versiones del maestro territorial del proyecto.

`chile_digital_inclusion_communes_2026.csv` es la base estructural. Tiene una fila por cada una de las 346 comunas de Chile y 38 campos públicos de identificación, conectividad, estructura territorial y contexto del hogar.

`chile_digital_inclusion_communes_2026_integrated.csv` conserva esas 346 filas y agrega la capa Ookla Open Data Q1 2026, junto con controles Q4 2025 → Q1 2026. El resultado tiene **65 variables**.

## Capa estructural

Incluye:

- códigos y nombres de región, provincia y comuna
- hogares totales y hogares válidos para la variable de Internet
- hogares sin Internet
- proxy de dependencia móvil
- teléfono móvil y computador
- Internet fija, móvil y satelital
- hogares urbanos y rurales
- hacinamiento y hacinamiento crítico
- tenencia de la vivienda
- hogares monoparentales
- hogares con niños, niñas y adolescentes
- hogares con personas mayores
- hogares con personas con discapacidad
- jefatura femenina
- hogares multigeneracionales
- macrozona operativa

Los porcentajes censales están expresados entre 0 y 100.

## Capa Ookla integrada

Para red fija y móvil se incorporan, cuando existe observación territorial:

- tiles asignados
- número de tests
- suma de dispositivos reportados por tile
- descarga y carga ponderadas por tests
- latencia y latencias cargadas
- número de tests del control Q4 2025
- variación porcentual Q4 2025 → Q1 2026 en descarga, carga y latencia

La asignación espacial usa el centroide del tile y el polígono comunal BCN. Ookla representa desempeño observado donde existieron tests; no equivale a cobertura comercial ni a una muestra probabilística de hogares.

## Llave territorial

El campo `comuna` es la llave principal y se relaciona con `geo/commune_codes.csv` y `geo/chile_communes.geojson`.

Antártica, código 12202, permanece en las 346 filas del maestro. La capa BCN utilizada por el proyecto no entrega un polígono para esa comuna, por lo que no se fabrica una geometría ni una observación Ookla territorial artificial.

## Diccionario

Las 65 variables del maestro integrado están documentadas en:

- `data/metadata/communal_master_dictionary.csv`
- `docs/communal_master_dictionary.md`

El diccionario registra fuente, unidad estadística, unidad de medida, denominador o ponderador y advertencias de comparabilidad.

## Uso recomendado

El maestro está diseñado como una base observable y reproducible para mapas, rankings descriptivos y cruces territoriales. No constituye por sí mismo un índice de vulnerabilidad ni una clasificación normativa de comunas.

No deben mezclarse mecánicamente porcentajes de hogares, estimaciones de encuestas y tests de red. Cada capa conserva su unidad estadística y su advertencia metodológica.

## Variables excluidas

La versión pública no incluye campos internos de índices habitacionales o de riesgo, escalas propietarias, `score_digital_presion`, segmentaciones derivadas, rankings propietarios ni ponderadores del Índice de Vulnerabilidad Digital.

## Fuentes

- Censo de Población y Vivienda 2024
- capa pública integrada del Atlas de la Desconexión Digital de Chile 2026
- Ookla Open Data Q4 2025 y Q1 2026
- Biblioteca del Congreso Nacional para cartografía comunal

Última revisión: 2026-08-13.
