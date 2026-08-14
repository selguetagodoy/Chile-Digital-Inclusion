# Diccionario del maestro comunal integrado

El archivo documenta **77 variables** del maestro `chile_digital_inclusion_communes_2026_integrated.csv`.

La tabla canónica y legible por máquinas está en `data/metadata/communal_master_dictionary.csv`.

## Principios

- una fila del maestro representa una comuna
- los porcentajes censales se mantienen separados de métricas de desempeño, registros de red y registros administrativos educativos
- Ookla se interpreta como desempeño observado donde existieron tests, no como cobertura probabilística
- los registros 4G/5G SUBTEL representan entidades puntuales publicadas por operador, no torres físicas únicas ni porcentaje de cobertura
- RedAcceso representa trazados regulatorios públicos y no disponibilidad comercial universal
- Aulas Conectadas representa selección administrativa de establecimientos y no conectividad efectiva del hogar
- la dependencia móvil es una proxy operacional del proyecto y no una categoría oficial del Censo
- no se publican ponderadores, scores ni el Índice de Vulnerabilidad Digital completo

## Variables por capa

- Censo/Atlas: 35
- Ookla Open Data: 27
- SUBTEL ArcGIS marzo 2025: 12
- Atlas derivado: 3

## Uso

Antes de construir rankings o modelos, revisar `statistical_unit`, `denominator_or_weight` y `comparability_note`. No deben mezclarse mecánicamente hogares censales, personas ponderadas de encuesta, tests de red, trazados regulatorios y registros de establecimientos.

Última revisión: 2026-08-14.
