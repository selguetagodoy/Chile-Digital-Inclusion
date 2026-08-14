# Chile Digital Inclusion

Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de evidencia de Censo 2024, CASEN 2024, SUBTEL y calidad observada de red.

El proyecto no trata acceso a Internet como sinónimo de inclusión digital. Mantiene separadas la desconexión dura, la dependencia móvil, la disponibilidad de Internet fijo, el equipamiento, las habilidades, los usos funcionales y el desempeño real de las redes.

## Cobertura actual

La versión pública contiene **40 archivos CSV**, documentación metodológica y scripts reproducibles para revisar cobertura, armonizar evidencia y actualizar la capa Ookla.

### Censo 2024 y Atlas público

La capa de hogares conserva el snapshot nacional, agregados regionales, casos urbanos de mayor volumen y variables de equipamiento y dependencia móvil.

En el snapshot nacional se mantienen 445.840 hogares sin Internet, una tasa de 6,8%, 64,2% con Internet fijo y 54,7% con computador. Las capas territoriales se publican como agregados y no incluyen registros individuales.

### CASEN Digital Master 2024

CASEN se mantiene como una capa de personas ponderadas y desigualdad social. Incluye estimación nacional, cuatro macrozonas, siete grupos de edad, 112 cruces región × edad, rankings regionales y comunales, las 52 comunas de la Región Metropolitana en variables de conectividad, conectividad por condición de pobreza, quintiles de ingreso, uso de Internet por sexo y un Top 30 de la brecha entre pobreza e Internet fijo.

La estimación nacional representa 20.131.682 personas. Registra 97,49% con algún acceso a Internet, 71,83% con fijo, 24,62% solo móvil y 2,51% sin Internet. La carencia de conectividad digital multidimensional alcanza 12,96% y la doble pobreza de ingresos y digital 4,15%.

| Macrozona | Fijo | Solo móvil | Sin Internet | Carencia digital | Doble pobreza |
|---|---:|---:|---:|---:|---:|
| Centro | 77,11% | 20,36% | 1,89% | 10,53% | 3,16% |
| Norte | 67,51% | 28,64% | 2,41% | 14,82% | 5,33% |
| Sur | 61,31% | 32,62% | 4,33% | 17,94% | 6,48% |
| Austral | 57,59% | 36,47% | 3,72% | 19,54% | 4,99% |

La brecha generacional también queda disponible como archivo. La carencia digital pasa de 9,43% en 30–44 años a 28,83% en 75+.

### SUBTEL — serie longitudinal 2015–2025

El repositorio incorpora una serie armonizada de las Encuestas de Acceso y Usos de Internet de SUBTEL. La capa longitudinal separa cinco dimensiones:

- acceso pagado del hogar y forma de conexión
- dispositivos utilizados para conectarse
- frecuencia de uso de Internet
- acceso en hogares compuestos solo por personas mayores
- habilidades digitales comparables entre 2023 y 2025

El acceso pagado del hogar aumenta desde 70,2% en 2015 hasta 96,6% en 2025. En paralelo, el acceso fijo total pasa de 48,8% a 74,6%. La dependencia de una conexión exclusivamente móvil alcanza 29,6% en 2017 y se sitúa en 21,8% en 2025.

La brecha territorial de acceso se reduce de manera importante en las olas comparables disponibles. En 2017 la encuesta registra 89,1% de acceso urbano y 76,7% rural. En 2025 los valores llegan a 96,8% y 95,1%, respectivamente.

Los hogares compuestos solo por personas mayores muestran una mejora desde 54,6% de acceso en 2017 a 83,2% en 2025. Aun así, en la última medición permanecen 13,4 puntos porcentuales bajo el promedio nacional del hogar.

La evolución de dispositivos muestra un cambio de estructura. El smartphone pasa de 90,0% en 2015 a 99,1% en 2025 y la TV conectada desde 19,0% a 77,5%. En el mismo período, el computador de escritorio cae desde 33,0% a 19,9%, mientras el portátil se mantiene en torno a seis de cada diez hogares conectados.

La dimensión de autonomía digital se observa desde 2023. Entre 2023 y 2025, la capacidad auto-reportada para usar procesador de texto sube de 53,3% a 59,4%; realizar transacciones bancarias, compras y pagos pasa de 63,5% a 71,7%; e instalar o configurar aplicaciones aumenta desde 49,7% a 52,3%. El uso de Inteligencia Artificial aparece como ítem recién en 2024, con 27,0%, y llega a 40,6% en 2025.

La serie no interpola años faltantes. También documenta los quiebres de cuestionario: la frecuencia de uso emplea una ventana de doce meses hasta 2023 y una ventana de tres meses desde 2024.

Archivos principales:

```text
data/subtel_longitudinal/
├── subtel_household_digital_access_2015_2025.csv
├── subtel_household_devices_2015_2025.csv
├── subtel_internet_use_frequency_2015_2025.csv
├── subtel_older_households_access_2017_2025.csv
└── subtel_digital_skills_2023_2025.csv
```

La metodología de armonización está documentada en `docs/subtel_longitudinal_methodology.md`.

### SUBTEL — última ola y estadísticas sectoriales

La Duodécima Encuesta fue publicada en 2026 con trabajo de campo 2025. Para esa ola se mantienen además tablas detalladas de acceso fijo/móvil, dispositivos, habilidades por edad, teletrabajo, postulación laboral, e-learning, interacción con el Estado y personas mayores.

También se incorporan series sectoriales SUBTEL de conexiones fijas y distribución por tramos de velocidad contratada. En septiembre de 2025 el stock alcanza 4.774.200 conexiones fijas y 63,77% se ubica sobre 100 Mbps y hasta 1 Gbps.

### Calidad observada — Ookla Q1 2026

El repositorio incorpora Q1 2026 de Chile desde los Parquet oficiales de Ookla Open Data. El pipeline filtra los tiles globales por centroide dentro del límite nacional y calcula los indicadores nacionales ponderando los promedios de cada tile por su número de tests.

| Red | Q4 2025 descarga | Q1 2026 descarga | Δ trimestral | Q1 carga | Q1 latencia |
|---|---:|---:|---:|---:|---:|
| Fija | 392,10 Mbps | 397,33 Mbps | +1,33% | 336,12 Mbps | 8,96 ms |
| Móvil | 105,66 Mbps | 98,87 Mbps | -6,43% | 21,43 Mbps | 33,71 ms |

La capa conserva además los tiles filtrados para permitir agregaciones regionales y comunales posteriores sin volver a descargar el parquet global.

## Estructura del repositorio

```text
Chile-Digital-Inclusion/
├── README.md
├── data/
│   ├── [30 CSV Censo, CASEN, SUBTEL y Atlas]
│   ├── subtel_longitudinal/
│   │   ├── subtel_household_digital_access_2015_2025.csv
│   │   ├── subtel_household_devices_2015_2025.csv
│   │   ├── subtel_internet_use_frequency_2015_2025.csv
│   │   ├── subtel_older_households_access_2017_2025.csv
│   │   └── subtel_digital_skills_2023_2025.csv
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
│   ├── sources.md
│   └── subtel_longitudinal_methodology.md
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

La serie longitudinal SUBTEL conserva los quiebres metodológicos en lugar de forzar continuidad estadística. Los faltantes se mantienen vacíos y las observaciones con cambios de definición contienen notas de comparabilidad.

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
