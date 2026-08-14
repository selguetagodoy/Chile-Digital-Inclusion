# Serie longitudinal SUBTEL 2015–2025

## Objetivo

Esta capa armoniza indicadores publicados en las Encuestas de Acceso y Usos de Internet de SUBTEL para observar cómo la brecha digital en Chile se desplaza desde el acceso básico hacia el tipo de conexión, los dispositivos y la autonomía de uso.

## Archivos

- `data/subtel_longitudinal/subtel_household_digital_access_2015_2025.csv`
- `data/subtel_longitudinal/subtel_household_devices_2015_2025.csv`
- `data/subtel_longitudinal/subtel_internet_use_frequency_2015_2025.csv`
- `data/subtel_longitudinal/subtel_older_households_access_2017_2025.csv`
- `data/subtel_longitudinal/subtel_digital_skills_2023_2025.csv`

## Regla de armonización

La serie conserva exclusivamente valores publicados por SUBTEL. No se interpolan años faltantes ni se reconstruyen categorías ausentes. Las celdas vacías representan información no comparable o no retenida con suficiente precisión en la fuente consultada.

Para acceso de hogares y formas de conexión se utiliza como referencia principal la serie histórica armonizada que SUBTEL reproduce en sus presentaciones más recientes. Esto evita mezclar cifras antiguas calculadas con factores de expansión distintos. En 2015 SUBTEL ajustó retrospectivamente resultados para mejorar comparabilidad con mediciones posteriores.

Las formas de acceso se expresan como porcentaje del total de hogares. Por efectos de redondeo, la suma de sus componentes puede diferir en una décima del porcentaje total publicado. Por ejemplo, los componentes de 2016 suman 79,4%, mientras la serie principal reporta 79,3% de hogares con acceso.

## Quiebres de comparabilidad

### Frecuencia de uso

Las mediciones 2015, 2016, 2017 y 2023 utilizan una ventana de referencia de doce meses. En 2024 la encuesta cambia a una ventana de tres meses. Por ello, el indicador de uso diario de 2024 y 2025 debe compararse con cautela respecto de las olas anteriores.

### Personas mayores

La categoría `Solo mayores` corresponde a una composición del hogar definida por cada presentación. La IX Encuesta explicita hogares compuestos únicamente por personas de 65 años o más. Las olas recientes mantienen una categoría equivalente, pero la serie se presenta como tendencia descriptiva y no como panel estadístico idéntico.

### Dispositivos

Los indicadores de dispositivos son de respuesta múltiple entre hogares con Internet. La aparición de nuevas categorías —como reproductores de streaming— refleja cambios del cuestionario y del ecosistema tecnológico. Los faltantes históricos se dejan vacíos.

### Habilidades digitales

La serie de habilidades comienza en 2023 porque las olas recientes contienen una batería suficientemente comparable. La pregunta mide capacidad auto-reportada para realizar tareas en smartphone o computador. El ítem de Inteligencia Artificial aparece por primera vez en 2024; por lo tanto, 2023 se mantiene sin dato.

## Lectura recomendada

La serie no debe resumirse en un único índice. El aumento del acceso puede coexistir con dependencia móvil, menor disponibilidad de computadores o brechas de habilidades. El propósito es mostrar esa transición desde conectividad nominal hacia autonomía digital efectiva.

## Fuente

Subsecretaría de Telecomunicaciones de Chile, Encuestas de Acceso y Usos de Internet. Catálogo oficial: `data/subtel_survey_catalog.csv`.

Última revisión: 2026-08-13.
