# Chile Digital Inclusion

Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de evidencia de Censo 2024, CASEN 2024, SUBTEL y calidad observada de red.

El proyecto no trata acceso a Internet como sinónimo de inclusión digital. Mantiene separadas la desconexión dura, la dependencia móvil, la disponibilidad de Internet fijo, el equipamiento, las habilidades, los usos funcionales y el desempeño real de las redes.

## Cobertura actual

La versión pública contiene **30 archivos CSV**, documentación metodológica y un script reproducible para revisar la cobertura de datos.

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

### Calidad observada

La capa Ookla se mantiene separada de las encuestas de acceso. Para Q4 2025, la red fija registra 391,9 Mbps de descarga, 332,6 Mbps de carga y 8,9 ms de latencia. La red móvil registra 105,5 Mbps, 23,2 Mbps y 30,9 ms.

## Estructura del repositorio

```text
Chile-Digital-Inclusion/
├── README.md
├── data/
│   ├── atlas_devices_mobile_snapshot.csv
│   ├── atlas_urban_volume_cases.csv
│   ├── casen_age_national_2024.csv
│   ├── casen_age_region_connectivity_2024.csv
│   ├── casen_commune_connectivity_rankings_2024.csv
│   ├── casen_commune_rankings_2024.csv
│   ├── casen_connectivity_by_income_quintile_2024.csv
│   ├── casen_connectivity_by_poverty_2024.csv
│   ├── casen_internet_use_by_sex_2024.csv
│   ├── casen_macrozones_2024.csv
│   ├── casen_national_2024.csv
│   ├── casen_poverty_fixed_gap_top30_2024.csv
│   ├── casen_region_rankings_2024.csv
│   ├── casen_rm_connectivity_2024.csv
│   ├── censo_atlas_regional_households_2024.csv
│   ├── national_snapshot_2026.csv
│   ├── network_quality_national_2025q4.csv
│   ├── reasons_no_fixed_internet_2024.csv
│   ├── source_registry.csv
│   ├── subtel_2025_access_modes.csv
│   ├── subtel_2025_devices_total.csv
│   ├── subtel_2025_digital_skills_basic.csv
│   ├── subtel_2025_digital_skills_intermediate.csv
│   ├── subtel_2025_learning_employment_by_age.csv
│   ├── subtel_2025_older_adults_summary.csv
│   ├── subtel_2025_state_interaction_by_sex.csv
│   ├── subtel_2025_telework_by_age.csv
│   ├── subtel_fixed_connections_series_2024_2025.csv
│   ├── subtel_fixed_speed_tiers_2025_09.csv
│   └── subtel_survey_catalog.csv
├── docs/
│   ├── data_dictionary.md
│   ├── key_findings.md
│   └── methodology.md
└── scripts/
    └── build_summary.py
```

## Cómo leer los datos

No deben compararse directamente universos distintos. Censo y las capas Atlas trabajan principalmente con hogares. CASEN utiliza personas ponderadas. SUBTEL utiliza hogares para acceso y personas de 16 años o más para sus módulos de uso. Ookla describe desempeño observado de red.

Las estimaciones comunales derivadas de encuestas deben interpretarse con cautela y junto al `N_ponderado` disponible. Para volumen e intensidad de desconexión comunal, la fuente estructural preferente es Censo 2024.

## Fuentes principales

- INE — Censo de Población y Vivienda 2024
- Ministerio de Desarrollo Social y Familia — CASEN 2024
- SUBTEL — Encuestas de Acceso y Usos de Internet y estadísticas sectoriales
- Ookla Open Data — calidad observada de red
- Atlas de la Desconexión Digital de Chile 2026 — capa integrada pública

## Frontera de publicación

La versión pública contiene datos agregados y trazables. No incorpora registros personales, identificadores directos, ponderadores internos, microdatos privados ni el Índice de Vulnerabilidad Digital completo.

## Autor

Sebastian Elgueta Godoy

Sociología, políticas públicas, telecomunicaciones e infraestructura digital.
