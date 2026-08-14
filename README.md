# Chile Digital Inclusion

Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de Censo 2024, CASEN 2024, Encuestas de Acceso y Usos de Internet de SUBTEL y calidad observada de red.

El proyecto no trata acceso a Internet como sinónimo de inclusión digital. Mantiene separadas la desconexión dura, el tipo de conexión, el equipamiento, las habilidades, los usos funcionales, las desigualdades sociales, la dimensión territorial y el desempeño de las redes.

## Cobertura actual

La versión pública combina evidencia censal, encuestas sociales y de telecomunicaciones, desempeño observado de red, cartografía comunal y pipelines reproducibles.

### Censo 2024 — 346 comunas

`data/censo_2024/` incorpora una capa pública comunal con las **346 comunas de Chile**.

`communes_connectivity_2024.csv` contiene 26 campos de identificación y conectividad por comuna: hogares totales, hogares sin Internet, dependencia móvil, teléfono móvil, computador, Internet fija, móvil y satelital, además de la composición urbano-rural.

`communes_social_context_2024.csv` agrega variables descriptivas del hogar y la vivienda: hacinamiento, tipo de tenencia, monoparentalidad, hogares con niños, niñas y adolescentes, personas mayores, discapacidad, jefatura femenina y hogares multigeneracionales.

La fuente es Censo 2024 y la capa pública integrada utilizada por el Atlas de la Desconexión Digital. `hogares_trampa_movil` es una proxy operacional del proyecto y no una categoría oficial del Censo.

### Maestro comunal integrado

`data/communal_master/chile_digital_inclusion_communes_2026.csv` es la base estructural de 346 comunas y 38 campos públicos.

`data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv` agrega desempeño Ookla fijo y móvil Q1 2026 y variaciones Q4 2025 → Q1 2026. Conserva las **346 comunas y llega a 65 variables**.

La versión pública excluye deliberadamente índices internos, scores, segmentaciones y ponderadores propietarios. El archivo es una base observable para mapas, rankings descriptivos y análisis reproducible; no es el Índice de Vulnerabilidad Digital.

Las 65 variables están documentadas en `data/metadata/communal_master_dictionary.csv` y `docs/communal_master_dictionary.md`, con fuente, unidad estadística, unidad de medida, denominador o ponderador y advertencia de comparabilidad.

### Geografía

`geo/commune_codes.csv` contiene el catálogo de las 346 comunas y su jerarquía región–provincia–comuna.

`geo/chile_communes.geojson` contiene la cartografía comunal ligera en WGS84 generada desde la capa pública División Comunal de la Biblioteca del Congreso Nacional. El servicio utilizado entrega 345 polígonos. La comuna de Antártica (12202) permanece en el catálogo y en la base comunal, pero no tiene geometría en esa fuente. La diferencia está documentada en `geo/geometry_coverage.csv` y no se completa con una geometría inventada.

### CASEN Digital Master 2024

CASEN se mantiene como una capa de personas ponderadas y desigualdad social. Incluye estimación nacional, cuatro macrozonas, siete grupos de edad, 112 cruces región × edad, rankings regionales y comunales, las 52 comunas de la Región Metropolitana en variables de conectividad, conectividad por condición de pobreza, quintiles de ingreso y uso de Internet por sexo.

La estimación nacional representa 20.131.682 personas. Registra 97,49% con algún acceso a Internet, 71,83% con fijo, 24,62% solo móvil y 2,51% sin Internet. La carencia de conectividad digital multidimensional alcanza 12,96%.

| Macrozona | Fijo | Solo móvil | Sin Internet | Carencia digital |
|---|---:|---:|---:|---:|
| Centro | 77,11% | 20,36% | 1,89% | 10,53% |
| Norte | 67,51% | 28,64% | 2,41% | 14,82% |
| Sur | 61,31% | 32,62% | 4,33% | 17,94% |
| Austral | 57,59% | 36,47% | 3,72% | 19,54% |

### SUBTEL — serie armonizada

El repositorio incorpora una serie longitudinal curada de acceso, formas de conexión, dispositivos, frecuencia de uso, personas mayores y habilidades digitales.

El acceso pagado del hogar aumenta desde 70,2% en 2015 hasta 96,6% en 2025. El acceso fijo total pasa de 48,8% a 74,6%. En las olas comparables, la brecha urbano-rural se reduce desde 89,1% versus 76,7% en 2017 hasta 96,8% versus 95,1% en 2025.

Los hogares compuestos solo por personas mayores pasan de 54,6% de acceso en 2017 a 83,2% en 2025. La serie de habilidades 2023–2025 muestra que la expansión del acceso no elimina las diferencias de autonomía digital.

Los archivos curados están en `data/subtel_longitudinal/`.

### SUBTEL — acceso segmentado

`data/subtel_segments/` reconstruye directamente desde los SAV oficiales el acceso propio y pagado a Internet en el hogar para 2015, 2016, 2017, 2023, 2024 y 2025.

El pipeline publica **127 tabulados agregados** y usa el factor de expansión de hogar específico de cada ola. Incluye:

- estimación nacional de control
- acceso por región en las seis olas
- acceso urbano/rural en las seis olas
- quintil/GSE en 2015–2017, cuando existe una categoría explícita verificable

Las cifras nacionales recalculadas reproducen la serie publicada con diferencias entre -0,31 y +0,05 puntos porcentuales. Para 2023–2025 no se reconstruyen quintiles desde tramos de ingreso cuando la base no entrega una categoría socioeconómica explícita y defendible.

### SUBTEL — procesamiento de bases oficiales

Además de las series curadas, el repositorio procesa directamente las bases públicas SPSS/SAV de SUBTEL. Actualmente cubre una base histórica de 2008 y las bases disponibles entre 2011 y 2025.

El pipeline descarga temporalmente las fuentes oficiales y publica únicamente resultados agregados. Los archivos originales no quedan almacenados en el repositorio.

La infraestructura ha inventariado:

- **4.844 variables** de cuestionarios y bases oficiales
- **7.743 filas categóricas agregadas** antes de la capa de ponderación
- **6.812 distribuciones con ponderación de hogar y/o persona** para las bases 2011–2025
- factores de expansión diferenciados por universo estadístico
- clasificación temática de miles de variables para construir series comparables
- supresión automática de categorías con menos de 30 casos sin ponderar

Directorios principales:

```text
data/subtel_longitudinal/    series curadas
data/subtel_segments/        acceso ponderado por región, zona y grupo socioeconómico verificable
data/subtel_microdata/       inventario, diccionario, distribuciones y crosswalk
data/subtel_weighted/        estimaciones ponderadas de hogar y persona
data/subtel_2008/            perfil agregado de la base histórica 2008
data/subtel_2011_person/     recuperación agregada del archivo de personas 2011
```

El catálogo de bases procesadas está en `data/subtel_microdata/processed_base_catalog.csv` y la metodología completa en `docs/subtel_microdata_pipeline.md`.

### Calidad observada — Ookla Q1 2026

El repositorio incorpora Q1 2026 de Chile desde los Parquet oficiales de Ookla Open Data. El pipeline filtra los tiles globales y calcula indicadores nacionales ponderados por número de tests.

| Red | Q4 2025 descarga | Q1 2026 descarga | Δ trimestral | Q1 carga | Q1 latencia |
|---|---:|---:|---:|---:|
| Fija | 392,10 Mbps | 397,33 Mbps | +1,33% | 336,12 Mbps | 8,96 ms |
| Móvil | 105,66 Mbps | 98,87 Mbps | -6,43% | 21,43 Mbps | 33,71 ms |

`data/ookla/territorial/` lleva la misma lógica al territorio. Q1 2026 contiene **683 filas comuna × red** y **32 filas región × red**. También se reconstruye Q4 2025 con la misma metodología para calcular cambios trimestrales.

La asignación espacial usa el centroide del tile dentro del polígono comunal BCN. El control de cobertura en `spatial_assignment_coverage.csv` muestra que aproximadamente 99% de los tests de las cuatro combinaciones período × red queda asignado a una comuna.

Ookla mide desempeño donde existieron tests. Complementa, pero no reemplaza, las fuentes de acceso, adopción y cobertura.

## Dashboard

El repositorio incluye una interfaz estática en:

```text
index.html
assets/dashboard.css
assets/dashboard.js
```

La vista carga el maestro comunal integrado y el GeoJSON, permite cambiar indicador, buscar comunas, revisar rankings y abrir una ficha territorial con conectividad, equipamiento, contexto social y desempeño Ookla.

El código está listo para alojamiento estático. La publicación mediante GitHub Pages requiere habilitar GitHub Actions como origen de Pages en la configuración del repositorio.

## Estructura analítica

```text
Chile-Digital-Inclusion/
├── index.html
├── assets/
│   ├── dashboard.css
│   └── dashboard.js
├── data/
│   ├── censo_2024/
│   ├── communal_master/
│   ├── metadata/
│   ├── casen_*.csv
│   ├── subtel_longitudinal/
│   ├── subtel_segments/
│   ├── subtel_microdata/
│   ├── subtel_weighted/
│   ├── subtel_2008/
│   ├── subtel_2011_person/
│   └── ookla/
│       └── territorial/
├── geo/
│   ├── commune_codes.csv
│   ├── chile_communes.geojson
│   └── geometry_coverage.csv
├── docs/
├── scripts/
└── .github/workflows/
```

## Reproducibilidad

Los workflows de GitHub Actions vuelven a descargar las fuentes públicas y reconstruyen los productos derivados. Para SUBTEL, los SAV/ZIP viven únicamente durante la ejecución del workflow. Para Ookla, los Parquet globales se descargan y se recortan a Chile. La cartografía comunal se reconstruye desde el servicio público de la Biblioteca del Congreso.

Los principales productos derivados tienen pipelines independientes para:

- descarga y perfilado de bases SUBTEL
- ponderación de hogar y persona
- clasificación y crosswalk de variables
- acceso SUBTEL segmentado
- descarga y control trimestral Ookla
- agregación Ookla comunal y regional
- cartografía comunal
- diccionario del maestro integrado

## Cómo leer los datos

No deben compararse directamente universos distintos. Censo trabaja principalmente con hogares. CASEN utiliza personas ponderadas. SUBTEL contiene preguntas de hogar y de persona dentro de una misma encuesta. Ookla representa tests observados.

Los faltantes se mantienen como faltantes. No se interpolan preguntas inexistentes ni se fuerza continuidad cuando cambia el cuestionario, el período de recuerdo o la población de referencia.

Las estimaciones territoriales de encuestas deben interpretarse considerando diseño muestral y tamaño efectivo. Para volumen estructural de desconexión territorial, Censo 2024 sigue siendo la referencia principal.

## Fuentes principales

- Instituto Nacional de Estadísticas — Censo de Población y Vivienda 2024
- Ministerio de Desarrollo Social y Familia — CASEN 2024
- Subsecretaría de Telecomunicaciones — Encuestas de Acceso y Usos de Internet y estadísticas sectoriales
- Biblioteca del Congreso Nacional — cartografía comunal
- Ookla Open Data — calidad observada de red
- Atlas de la Desconexión Digital de Chile 2026 — capa integrada pública

## Frontera de publicación

La versión pública contiene datos agregados y trazables. No incorpora registros personales, identificadores directos, respuestas abiertas, microdatos originales de encuesta, índices internos ni el Índice de Vulnerabilidad Digital completo.

Los datos derivados de Ookla en `data/ookla/` se mantienen bajo los términos de licencia de la fuente.

## Autor

Sebastian Elgueta Godoy

Sociología, políticas públicas, telecomunicaciones e infraestructura digital.
