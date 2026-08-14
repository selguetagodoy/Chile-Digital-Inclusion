# Asequibilidad digital — evidencia SUBTEL

Esta carpeta incorpora una dimensión de asequibilidad construida directamente desde las encuestas oficiales SUBTEL 2023, 2024 y 2025.

## Qué mide

`subtel_willingness_to_pay_2023_2025.csv` resume el **máximo monto declarado que las personas/hogares estarían dispuestos a pagar** por una conexión a Internet. Se publican media, mediana y percentiles ponderados usando el factor de hogar de cada ola.

Esto **no es el precio de mercado, la tarifa contratada ni el gasto real del hogar**. Es una medida declarada de disposición máxima a pagar y debe interpretarse como evidencia de asequibilidad desde la demanda.

`subtel_cost_barriers_2023_2025.csv` mide tres razones declaradas dentro del universo de hogares que responde por qué no tiene banda ancha fija propia y pagada:

- costo del equipo o terminal demasiado alto
- costo del servicio fijo demasiado alto
- Internet fija más cara que Internet móvil

El denominador es el universo que responde el bloque P13, no el total de hogares de Chile.

## Reglas

- se usa el factor de expansión de hogares de cada encuesta
- no se almacenan microdatos SAV en GitHub
- se excluyen NS/NR y valores monetarios no positivos
- se suprimen resultados con menos de 30 observaciones válidas sin ponderar
- no se construye un índice de asequibilidad ni se divide por ingreso sin una definición longitudinal homogénea del denominador

## Comparabilidad

En 2024 y 2025 las preguntas Q42/Q42.1 distinguen Internet fija e Internet móvil en el hogar. En 2023 Q42 pregunta por un servicio de conexión a Internet sin esa misma separación; por eso se conserva como `internet_connection_unspecified` y no se fuerza a la serie fija.

Las tres barreras P13 seleccionadas mantienen una formulación suficientemente equivalente en 2023–2025 para presentarlas juntas, pero sus porcentajes describen el universo específico de no contratación de banda ancha fija.

`affordability_mapping_manifest.csv` registra variables, ponderadores, fuente y archivo SAV utilizado.

Última revisión: 2026-08-13.
