# Chile Digital Inclusion

Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de evidencia de Censo 2024, CASEN 2024, SUBTEL y calidad observada de red.

El proyecto no trata acceso a Internet como sinónimo de inclusión digital. Mantiene separadas la desconexión dura, la dependencia móvil, la disponibilidad de Internet fijo, los dispositivos, las barreras de adopción y el desempeño real de las redes.

## Qué contiene hoy

La versión pública ya incorpora cuatro capas distintas.

### Censo 2024 y Atlas público

A escala de hogares, el snapshot nacional retiene 445.840 hogares sin Internet, una tasa de 6,8%, 64,2% con Internet fijo y 54,7% con computador. La capa regional muestra que La Araucanía y Ñuble alcanzan 12,9% de hogares sin Internet, mientras la Región Metropolitana concentra el mayor volumen absoluto entre las regiones retenidas, con 114.655 hogares.

### CASEN Digital Master 2024

CASEN se mantiene como una capa de personas ponderadas, no de hogares. La estimación nacional representa 20.131.682 personas y registra 97,49% con algún acceso a Internet, 71,83% con fijo, 24,62% solo móvil y 2,51% sin Internet. La carencia de conectividad digital multidimensional alcanza 12,96% y la doble pobreza de ingresos y digital 4,15%.

Las cuatro macrozonas muestran una gradiente clara.

| Macrozona | Fijo | Solo móvil | Sin Internet | Carencia digital | Doble pobreza |
|---|---:|---:|---:|---:|---:|
| Centro | 77,11% | 20,36% | 1,89% | 10,53% | 3,16% |
| Norte | 67,51% | 28,64% | 2,41% | 14,82% | 5,33% |
| Sur | 61,31% | 32,62% | 4,33% | 17,94% | 6,48% |
| Austral | 57,59% | 36,47% | 3,72% | 19,54% | 4,99% |

El repositorio incluye además rankings regionales y rankings comunales restringidos a variables de conectividad. Esto permite mostrar territorios con alta dependencia solo móvil o muy baja penetración fija sin publicar el modelo completo de vulnerabilidad.

### SUBTEL

La serie oficial de Encuestas de Acceso y Usos de Internet se mantiene como una fuente propia. El catálogo público incluye la Duodécima Encuesta, publicada bajo 2026 con trabajo de campo 2025, junto con la Undécima, Décima y olas anteriores.

La Duodécima Encuesta utilizó 5.000 entrevistas presenciales en zonas urbanas y rurales de las 16 regiones. La sección de acceso se refiere a hogares y la sección de uso a personas de 16 años o más.

Para 2025, 96,6% de los hogares declara acceso propio y pagado a Internet fijo o móvil. La cifra llega a 96,8% en urbano y 95,1% en rural, pero baja a 83,2% entre hogares compuestos solo por personas mayores. El acceso fijo total, considerando fijo solo o combinado con móvil, alcanza 74,6%.

En formas de acceso pagado, 66,8% corresponde a fijo solamente, 21,8% a móvil solamente y 7,8% a la combinación fijo + móvil.

En dispositivos de acceso del hogar, SUBTEL 2025 registra smartphone 99,1%, TV conectada 77,5%, computador portátil 61,0%, tablet 24,9%, reproductor de streaming 22,7%, consola 22,0% y computador fijo 19,9%.

### Calidad observada

La capa de desempeño mantiene separado el acceso de la experiencia de uso. Para Q4 2025, la red fija registra 391,9 Mbps de descarga, 332,6 Mbps de carga y 8,9 ms de latencia. La red móvil registra 105,5 Mbps, 23,2 Mbps y 30,9 ms.

## Archivos publicados

```text
Chile-Digital-Inclusion/
├── README.md
├── data/
│   ├── national_snapshot_2026.csv
│   ├── casen_national_2024.csv
│   ├── casen_macrozones_2024.csv
│   ├── casen_region_rankings_2024.csv
│   ├── casen_commune_connectivity_rankings_2024.csv
│   ├── censo_atlas_regional_households_2024.csv
│   ├── network_quality_national_2025q4.csv
│   ├── reasons_no_fixed_internet_2024.csv
│   ├── subtel_survey_catalog.csv
│   ├── subtel_2025_devices_total.csv
│   └── subtel_2025_access_modes.csv
└── docs/
    └── methodology.md
```

## Cómo leer los datos

No deben compararse directamente universos distintos. Censo/Atlas trabaja principalmente con hogares. CASEN utiliza personas ponderadas. SUBTEL usa hogares para acceso y personas de 16 años o más para la sección de usos. Ookla describe desempeño de red.

Por esa razón, 6,8% de hogares sin Internet en el agregado Censo/Atlas y 2,51% de personas sin Internet en CASEN no son cifras contradictorias: responden a unidades y diseños estadísticos distintos.

Las estimaciones comunales derivadas de encuesta deben interpretarse con cautela y siempre junto al `N_ponderado` disponible.

## Fuentes

- INE — Censo de Población y Vivienda 2024
- Ministerio de Desarrollo Social y Familia — CASEN 2024
- SUBTEL — Encuestas de Acceso y Usos de Internet
- Ookla Open Data — calidad observada de red

Fuente SUBTEL: https://www.subtel.gob.cl/estudios/internet-y-sociedad-de-la-informacion/

## Frontera de publicación

La versión pública contiene datos agregados y trazables. No incorpora registros personales, identificadores directos, ponderadores internos ni el Índice de Vulnerabilidad Digital completo.

## Autor

Sebastian Elgueta Godoy

Sociología, políticas públicas, telecomunicaciones e infraestructura digital.
