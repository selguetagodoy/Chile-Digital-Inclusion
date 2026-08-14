# Chile Digital Inclusion — maestro comunal público

`chile_digital_inclusion_communes_2026.csv` es la tabla territorial base del proyecto. Contiene una fila por cada una de las 346 comunas de Chile y 38 campos públicos de identificación, conectividad, estructura territorial y contexto del hogar.

## Qué incluye

La tabla integra:

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

Los porcentajes están expresados entre 0 y 100.

## Uso recomendado

El campo `comuna` funciona como llave territorial para unir esta tabla con `geo/commune_codes.csv`, la cartografía comunal y futuras capas de Ookla, SUBTEL o CASEN que tengan una unidad territorial compatible.

El archivo está diseñado como una base observable y reproducible para mapas, rankings descriptivos y cruces territoriales. No constituye por sí mismo un índice de vulnerabilidad ni una clasificación normativa de comunas.

## Variables excluidas

La versión pública no incluye los campos internos de índices habitacionales o de riesgo, escalas propietarias, `score_digital_presion`, segmentaciones derivadas, rankings propietarios ni ponderadores del Índice de Vulnerabilidad Digital.

## Fuente

Censo de Población y Vivienda 2024 / capa pública integrada del Atlas de la Desconexión Digital de Chile 2026.

Última revisión: 2026-08-13.
