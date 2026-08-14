# Censo 2024 — capa comunal pública

Esta carpeta contiene una versión pública y sanitizada de la capa comunal utilizada por Chile Digital Inclusion. La unidad principal son hogares y el universo territorial cubre las 346 comunas del país.

## Archivos

### `communes_connectivity_2024.csv`

Una fila por comuna con 26 campos de identificación y conectividad. Incluye hogares totales, hogares válidos para la variable de Internet, hogares sin Internet, disponibilidad de teléfono móvil y computador, Internet fija, móvil y satelital, y distribución urbano-rural. Las tasas están expresadas en porcentaje de 0 a 100.

`hogares_trampa_movil_n` y `hogares_trampa_movil_pct` son una proxy operacional del proyecto para identificar hogares con dependencia móvil. No corresponden a una categoría oficial publicada por el Censo.

### `communes_social_context_2024.csv`

Una fila por comuna con variables agregadas de contexto habitacional y del hogar: hacinamiento, no propiedad, arriendo, tenencia irregular, monoparentalidad, hogares con niños, niñas y adolescentes, personas mayores, discapacidad, jefatura femenina y hogares multigeneracionales.

## Fuentes y alcance

La capa deriva del Censo de Población y Vivienda 2024 y de la integración pública utilizada en el Atlas de la Desconexión Digital. Por esa razón, no debe asumirse que cada columna es una variable directa del archivo censal original sin transformación.

INE publica resultados censales, bases y herramientas territoriales en:

https://censo2024.ine.gob.cl/resultados/

## Frontera de publicación

Esta carpeta excluye expresamente índices compuestos, ponderaciones internas, scores de presión digital, segmentos propietarios y el Índice de Vulnerabilidad Digital. Solo se publican observaciones agregadas o variables descriptivas.

Última revisión: 2026-08-13.
