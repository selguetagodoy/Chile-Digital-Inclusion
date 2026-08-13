# Chile Digital Inclusion

Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de evidencia territorial y social.

El proyecto separa dos unidades que no deben confundirse. Censo 2024 y el Atlas permiten analizar principalmente hogares y territorio. CASEN 2024 permite analizar personas ponderadas y brechas sociales por edad, pobreza, región y tipo de acceso.

## CASEN Digital Master 2024

La capa CASEN incorporada al proyecto contiene ocho módulos analíticos:

- nacional
- macrozonas
- rankings regionales
- rankings comunales
- detalle de las 52 comunas de la Región Metropolitana
- indicadores nacionales por edad
- indicadores región × edad
- brecha comunal entre pobreza por ingresos e Internet fijo

La base nacional pondera 20.131.682 personas. Registra 97,49% con algún acceso a Internet, 71,83% con Internet fijo, 24,62% solo móvil y 2,51% sin Internet. La carencia de conectividad digital multidimensional alcanza 12,96%, mientras que la doble pobreza de ingresos y digital llega a 4,15%.

## Lectura territorial

| Macrozona | Internet fijo | Solo móvil | Sin Internet | Carencia digital |
|---|---:|---:|---:|---:|
| Centro | 77,11% | 20,36% | 1,89% | 10,53% |
| Norte | 67,51% | 28,64% | 2,41% | 14,82% |
| Sur | 61,31% | 32,62% | 4,33% | 17,94% |
| Austral | 57,59% | 36,47% | 3,72% | 19,54% |

## Brecha generacional

| Edad | Internet fijo | Solo móvil | Sin Internet | Carencia digital |
|---|---:|---:|---:|---:|
| 15–29 | 75,33% | 22,89% | 0,82% | 10,40% |
| 30–44 | 75,78% | 22,34% | 0,90% | 9,43% |
| 45–59 | 70,70% | 25,72% | 2,47% | 13,18% |
| 60–74 | 64,77% | 28,87% | 5,30% | 18,46% |
| 75+ | 54,41% | 29,99% | 14,41% | 28,83% |

La caída con la edad no aparece solo en acceso. También aumenta la dependencia móvil y la carencia digital, lo que permite analizar autonomía y no únicamente cobertura.

## Fuentes principales

- Censo de Población y Vivienda 2024 — INE
- CASEN 2024 — Ministerio de Desarrollo Social y Familia
- SUBTEL — estadísticas de conectividad y dispositivos
- Ookla Open Data — calidad de servicio cuando corresponde
- Elaboración propia a partir de bases públicas consolidadas

## Estructura pública

```text
Chile-Digital-Inclusion/
├── README.md
├── data/
│   └── national_snapshot_2026.csv
└── docs/
    └── methodology.md
```

La próxima capa pública está diseñada para incorporar los ocho módulos agregados del CASEN Digital Master sin publicar registros individuales ni identificadores personales.

## Principios de publicación

El repositorio mantiene separadas las unidades de análisis, conserva datos faltantes cuando corresponde y no publica microdatos personales, el Índice de Vulnerabilidad Digital completo, ponderadores propietarios ni modelos comerciales.

## Autor

Sebastian Elgueta Godoy

Sociología, políticas públicas, telecomunicaciones e infraestructura digital.
