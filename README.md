# Chile Digital Inclusion

Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de Censo 2024, CASEN 2024, Encuestas de Acceso y Usos de Internet de SUBTEL y calidad observada de red.

El proyecto no trata acceso a Internet como sinónimo de inclusión digital. Mantiene separadas la desconexión dura, el tipo de conexión, el equipamiento, las habilidades, los usos funcionales, las desigualdades sociales y el desempeño de las redes.

## Cobertura actual

La versión pública combina cuatro capas complementarias.

### Censo 2024 y Atlas público

La capa de hogares conserva el snapshot nacional, agregados regionales, casos territoriales y variables de equipamiento y dependencia móvil.

En el snapshot nacional se mantienen 445.840 hogares sin Internet, una tasa de 6,8%, 64,2% con Internet fijo y 54,7% con computador. Los datos territoriales se publican como agregados y no incluyen registros individuales.

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

Los archivos curados están en:

```text
data/subtel_longitudinal/
```

### SUBTEL — procesamiento de bases oficiales

Además de la serie curada, el repositorio procesa directamente las bases públicas SPSS/SAV de SUBTEL. Actualmente cubre la base histórica de 2008 y las bases disponibles entre 2011 y 2025.

El pipeline descarga temporalmente las fuentes oficiales y publica únicamente resultados agregados. Los archivos originales no quedan almacenados en el repositorio.

La infraestructura de procesamiento ya inventaría:

- **4.844 variables** de cuestionarios y bases oficiales
- **7.743 filas categóricas agregadas** antes de la capa de ponderación
- **6.812 distribuciones con ponderación de hogar y/o persona** para las bases 2011–2025
- factores de expansión diferenciados por universo estadístico
- clasificación temática de miles de variables para construir series comparables
- supresión automática de categorías con menos de 30 casos sin ponderar

Directorios principales:

```text
data/subtel_microdata/      inventario, diccionario, distribuciones y crosswalk
data/subtel_weighted/       estimaciones ponderadas de hogar y persona
data/subtel_2008/           perfil agregado de la base histórica 2008
data/subtel_2011_person/    recuperación del archivo de personas 2011
```

El catálogo de bases procesadas está en `data/subtel_microdata/processed_base_catalog.csv` y la metodología completa en `docs/subtel_microdata_pipeline.md`.

Entre los dominios detectados para armonización están acceso del hogar, Internet fijo y móvil, región, ruralidad, edad, sexo, ingresos/GSE, dispositivos, motivos de no acceso, habilidades, banca y pagos, Estado digital, educación, trabajo, seguridad, discapacidad y pueblos originarios.

La clasificación automática sirve para localizar preguntas equivalentes; no convierte por sí sola dos preguntas en una serie comparable. La homologación final exige revisar concepto, universo y categorías en cada cuestionario.

### Calidad observada — Ookla Q1 2026

El repositorio incorpora Q1 2026 de Chile desde los Parquet oficiales de Ookla Open Data. El pipeline filtra los tiles globales y calcula indicadores nacionales ponderados por número de tests.

| Red | Q4 2025 descarga | Q1 2026 descarga | Δ trimestral | Q1 carga | Q1 latencia |
|---|---:|---:|---:|---:|---:|
| Fija | 392,10 Mbps | 397,33 Mbps | +1,33% | 336,12 Mbps | 8,96 ms |
| Móvil | 105,66 Mbps | 98,87 Mbps | -6,43% | 21,43 Mbps | 33,71 ms |

La capa conserva además los tiles de Chile para permitir futuras agregaciones regionales y comunales.

## Estructura analítica

```text
Chile-Digital-Inclusion/
├── data/
│   ├── casen_*.csv
│   ├── censo_*.csv
│   ├── subtel_*.csv
│   ├── subtel_longitudinal/
│   ├── subtel_microdata/
│   ├── subtel_weighted/
│   ├── subtel_2008/
│   ├── subtel_2011_person/
│   └── ookla/
├── docs/
│   ├── methodology.md
│   ├── data_dictionary.md
│   ├── subtel_longitudinal_methodology.md
│   ├── subtel_microdata_pipeline.md
│   └── ookla_open_data.md
├── scripts/
│   ├── build_ookla_chile_quarter.py
│   ├── profile_subtel_microdata.py
│   ├── build_subtel_weighted_profiles.py
│   ├── classify_subtel_variables.py
│   ├── build_subtel_crosswalk.py
│   ├── profile_subtel_2008.py
│   └── profile_subtel_2011_person.py
└── .github/workflows/
```

## Reproducibilidad

Los workflows de GitHub Actions vuelven a descargar las fuentes públicas y reconstruyen los productos derivados. Para SUBTEL, los SAV/ZIP/RAR viven únicamente durante la ejecución del workflow. Para Ookla, los Parquet globales se descargan y se recortan a Chile.

## Cómo leer los datos

No deben compararse directamente universos distintos. Censo trabaja principalmente con hogares. CASEN utiliza personas ponderadas. SUBTEL contiene preguntas de hogar y de persona dentro de una misma encuesta. Por esa razón el pipeline conserva por separado los factores de expansión correspondientes a cada universo.

Los faltantes se mantienen como faltantes. No se interpolan preguntas inexistentes ni se fuerza continuidad cuando cambia el cuestionario, el período de recuerdo o la población de referencia.

Las estimaciones territoriales de encuestas deben interpretarse considerando diseño muestral y tamaño efectivo. Para volumen estructural de desconexión territorial, Censo 2024 sigue siendo la referencia principal.

Ookla mide desempeño donde existieron tests. Complementa, pero no reemplaza, las fuentes de acceso y adopción.

## Fuentes principales

- Instituto Nacional de Estadísticas — Censo de Población y Vivienda 2024
- Ministerio de Desarrollo Social y Familia — CASEN 2024
- Subsecretaría de Telecomunicaciones — Encuestas de Acceso y Usos de Internet y estadísticas sectoriales
- Ookla Open Data — calidad observada de red
- Atlas de la Desconexión Digital de Chile 2026 — capa integrada pública

## Frontera de publicación

La versión pública contiene datos agregados y trazables. No incorpora registros personales, identificadores directos, respuestas abiertas, microdatos originales de encuesta ni el Índice de Vulnerabilidad Digital completo.

Los datos derivados de Ookla en `data/ookla/` se mantienen bajo los términos de licencia de la fuente.

## Autor

Sebastian Elgueta Godoy

Sociología, políticas públicas, telecomunicaciones e infraestructura digital.
