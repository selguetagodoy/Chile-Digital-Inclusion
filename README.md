# Chile Digital Inclusion

Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de evidencia de Censo 2024, CASEN 2024, SUBTEL y calidad observada de red.

El proyecto no trata acceso a Internet como sinónimo de inclusión digital. Mantiene separadas la desconexión dura, la dependencia móvil, la disponibilidad de Internet fijo, el equipamiento, las habilidades, los usos funcionales y el desempeño real de las redes.

## Cobertura actual

La versión pública contiene **35 archivos CSV**, documentación metodológica y scripts reproducibles para revisar cobertura y actualizar la capa Ookla.

### Censo 2024 y Atlas público

La capa de hogares conserva el snapshot nacional, agregados regionales, casos urbanos de mayor volumen y variables de equipamiento y dependencia móvil.

En el snapshot nacional se mantienen 445.840 hogares sin Internet, una tasa de 6,8%, 64,2% con Internet fijo y 54,7% con computador. Las capas territoriales se publican como agregados y no incluyen registros individuales.

### CASEN Digital Master 2024

CASEN se mantiene como una capa de personas ponderadas y desigualdad social. Incluye:

- estimación nacional
- cuatro macrozonas
- siete grupos de edad
- 112 cruces región × edad para conectividad
- rankings regionales
- rankings comunales de conectividad y vulnerabilidad agregada
- las 52 comunas de la Región Metropolitana en variables de conectividad
- conectividad por condición de pobreza
- conectividad por quintil de ingresos
- uso de Internet por sexo
- Top 30 de la brecha entre pobreza por ingresos e Internet fijo

La estimación nacional representa 20.131.682 personas. Registra 97,49% con algún acceso a Internet, 71,83% con fijo, 24,62% solo móvil y 2,51% sin Internet. La carencia de conectividad digital multidimensional alcanza 12,96% y la doble pobreza de ingresos y digital 4,15%.

| Macrozona | Fijo | Solo móvil | Sin Internet | Carencia digital | Doble pobreza |
|---|---:|---:|---:|---:|---:|
| Centro | 77,11% | 20,36% | 1,89% | 10,53% | 3,16% |
| Norte | 67,51% | 28,64% | 2,41% | 14,82% | 5,33% |
| Sur | 61,31% | 32,62% | 4,33% | 17,94% | 6,48% |
| Austral | 57,59% | 36,47% | 3,72% | 19,54% | 4,99% |

La brecha generacional también queda disponible como archivo. La carencia digital pasa de 9,43% en 30–44 años a 28,83% en 75+.

### SUBTEL

La serie oficial de Encuestas de Acceso y Usos de Internet se mantiene como una capa propia. El catálogo incorporado cubre las publicaciones disponibles desde 2008 hasta la Duodécima Encuesta publicada en 2026 con trabajo de campo 2025.

Para la Duodécima Encuesta se publican tablas agregadas de:

- acceso pagado y modalidades fijo/móvil
- dispositivos utilizados en el hogar
- habilidades digitales básicas por edad
- habilidades digitales intermedias por edad
- teletrabajo por edad
- postulación laboral y e-learning por edad
- interacción con el Estado por sexo
- indicadores específicos de personas mayores

Para 2025, 96,6% de los hogares declara acceso propio y pagado a Internet fijo o móvil. Entre hogares compuestos solo por personas mayores la cifra baja a 83,2%.

También se incorporan series sectoriales SUBTEL de conexiones fijas y distribución por tramos de velocidad contratada. En septiembre de 2025 el stock alcanza 4.774.200 conexiones fijas y 63,77% se ubica sobre 100 Mbps y hasta 1 Gbps.

### Calidad observada — Ookla Q1 2026

El repositorio ya incorpora **Q1 2026 de Chile** desde los Parquet oficiales de Ookla Open Data. El pipeline filtra los tiles globales por centroide dentro del límite nacional y calcula los indicadores nacionales ponderando los promedios de cada tile por su número de tests.

| Red | Q4 2025 descarga | Q1 2026 descarga | Δ trimestral | Q1 carga | Q1 latencia |
|---|---:|---:|---:|---:|---:|
| Fija | 392,10 Mbps | 397,33 Mbps | +1,33% | 336,12 Mbps | 8,96 ms |
| Móvil | 105,66 Mbps | 98,87 Mbps | -6,43% | 21,43 Mbps | 33,71 ms |

La red fija mejora levemente en descarga y carga. En móvil, Q1 2026 muestra una caída de 6,43% en descarga y 7,57% en carga respecto de Q4 2025, junto con un aumento de 10,04% en latencia.

Q1 2026 contiene 29.232 tiles fijos con 517.216 tests y 22.938 tiles móviles con 125.101 tests después del recorte espacial de Chile.

La capa conserva además los tiles filtrados para permitir agregaciones regionales y comunales posteriores sin volver a descargar el parquet global.

## Estructura del repositorio

```text
Chile-Digital-Inclusion/
├── README.md
├── data/
│   ├── [30 CSV Censo, CASEN, SUBTEL y Atlas]
│   └── ookla/
│       ├── chile_2025q4_control_summary.csv
│       ├── chile_2025q4_vs_2026q1.csv
│       ├── chile_2026q1_fixed_tiles.csv
│       ├── chile_2026q1_mobile_tiles.csv
│       └── chile_2026q1_summary.csv
├── docs/
│   ├── data_dictionary.md
│   ├── key_findings.md
│   ├── methodology.md
│   ├── ookla_open_data.md
│   └── sources.md
├── scripts/
│   ├── build_summary.py
│   └── build_ookla_chile_quarter.py
└── .github/workflows/
    └── build-ookla-chile-q1-2026.yml
```

## Reproducibilidad

El pipeline de Ookla se ejecuta con GitHub Actions y deja los resultados derivados en `data/ookla/`. Para reproducir otro trimestre:

```bash
python scripts/build_ookla_chile_quarter.py --year 2026 --quarter 1 --compare-year 2025 --compare-quarter 4
```

## Cómo leer los datos

No deben compararse directamente universos distintos. Censo y las capas Atlas trabajan principalmente con hogares. CASEN utiliza personas ponderadas. SUBTEL utiliza hogares para acceso y personas de 16 años o más para sus módulos de uso. Ookla describe desempeño observado de red.

Las estimaciones comunales derivadas de encuestas deben interpretarse con cautela y junto al `N_ponderado` disponible. Para volumen e intensidad de desconexión comunal, la fuente estructural preferente es Censo 2024.

Ookla no mide acceso universal. Los tiles representan desempeño donde existieron tests y por eso complementan, pero no reemplazan, las fuentes estructurales.

## Fuentes principales

- INE — Censo de Población y Vivienda 2024
- Ministerio de Desarrollo Social y Familia — CASEN 2024
- SUBTEL — Encuestas de Acceso y Usos de Internet y estadísticas sectoriales
- Ookla Open Data — calidad observada de red
- Atlas de la Desconexión Digital de Chile 2026 — capa integrada pública

## Frontera de publicación

La versión pública contiene datos agregados y trazables. No incorpora registros personales, identificadores directos, ponderadores internos, microdatos privados ni el Índice de Vulnerabilidad Digital completo.

Los datos derivados de Ookla en `data/ookla/` se mantienen bajo los términos CC BY-NC-SA 4.0 de la fuente y no bajo una eventual licencia de código del repositorio.

## Autor

Sebastian Elgueta Godoy

Sociología, políticas públicas, telecomunicaciones e infraestructura digital.
