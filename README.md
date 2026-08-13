# Chile Digital Inclusion

Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de evidencia territorial y social.

El proyecto separa dos unidades que no deben confundirse. Censo 2024 y el Atlas permiten analizar principalmente hogares y territorio. CASEN 2024 permite analizar personas ponderadas y brechas sociales por edad, pobreza, región y tipo de acceso.

## CASEN Digital Master 2024

La capa CASEN contiene ocho módulos analíticos:

- nacional
- macrozonas
- rankings regionales
- rankings comunales
- detalle de las 52 comunas de la Región Metropolitana
- indicadores nacionales por edad
- indicadores región × edad
- brecha comunal entre pobreza por ingresos e Internet fijo

La base nacional pondera **20.131.682 personas**. Registra **97,49%** con algún acceso a Internet, **71,83%** con Internet fijo, **24,62%** solo móvil y **2,51%** sin Internet. La carencia de conectividad digital multidimensional alcanza **12,96%**, mientras la doble pobreza de ingresos y digital llega a **4,15%**.

## Lectura territorial

| Macrozona | Internet fijo | Solo móvil | Sin Internet | Carencia digital | Doble pobreza |
|---|---:|---:|---:|---:|---:|
| Centro | 77,11% | 20,36% | 1,89% | 10,53% | 3,16% |
| Norte | 67,51% | 28,64% | 2,41% | 14,82% | 5,33% |
| Sur | 61,31% | 32,62% | 4,33% | 17,94% | 6,48% |
| Austral | 57,59% | 36,47% | 3,72% | 19,54% | 4,99% |

La brecha territorial aparece incluso cuando el acceso general supera 95% en todas las macrozonas. Lo que cambia es la calidad funcional del acceso: fijo, dependencia móvil y carencia multidimensional.

## Brecha generacional

| Edad | Internet fijo | Solo móvil | Sin Internet | Carencia digital |
|---|---:|---:|---:|---:|
| 15–29 | 75,33% | 22,89% | 0,82% | 10,40% |
| 30–44 | 75,78% | 22,34% | 0,90% | 9,43% |
| 45–59 | 70,70% | 25,72% | 2,47% | 13,18% |
| 60–74 | 64,77% | 28,87% | 5,30% | 18,46% |
| 75+ | 54,41% | 29,99% | 14,41% | 28,83% |

La caída con la edad no aparece solo en acceso. También aumenta la dependencia móvil y la carencia digital, lo que permite analizar autonomía y no únicamente cobertura.

## Regiones con mayor presión digital

| Indicador | 1° | 2° | 3° | 4° | 5° |
|---|---|---|---|---|---|
| Carencia digital | Ñuble 24,95% | Los Lagos 22,53% | Atacama 21,90% | La Araucanía 21,57% | O'Higgins 18,66% |
| Solo móvil | La Araucanía 44,20% | Los Lagos 41,63% | Atacama 37,98% | Maule 35,31% | Los Ríos 34,93% |
| Sin Internet | Ñuble 7,03% | La Araucanía 5,75% | Maule 4,54% | Los Lagos 4,13% | Aysén 3,93% |
| Doble pobreza | La Araucanía 9,35% | Ñuble 8,57% | Atacama 6,44% | Coquimbo 6,19% | Los Ríos 6,19% |

## Comunas que muestran la brecha más dura

La carencia digital multidimensional alcanza sus valores más altos en **Camiña 84,51%**, **Cobquecura 73,93%**, **Colchane 73,41%**, **Lumaco 71,98%** y **Alto Biobío 70,86%**.

La doble pobreza de ingresos y digital se concentra especialmente en **Galvarino 35,67%**, **Lumaco 32,50%**, **Alto Biobío 31,82%**, **San Ignacio 27,81%** y **Teodoro Schmidt 27,16%**.

La dependencia solo móvil llega a **91,29% en Huara**, **90,83% en Putre**, **89,91% en Torres del Paine**, **85,00% en General Lagos** y **81,39% en Alto del Carmen**.

## Región Metropolitana

El detalle de las 52 comunas muestra que la brecha también existe dentro del principal mercado digital del país. En doble pobreza lideran **San José de Maipo 11,32%**, **Melipilla 9,27%**, **Lampa 8,00%**, **Tiltil 7,85%** y **Curacaví 7,05%**. San Pedro destaca además por una combinación particularmente frágil de baja penetración fija y alta dependencia móvil.

## Pobreza e Internet fijo

El maestro incluye 333 comunas con una medida descriptiva de brecha entre pobreza por ingresos y penetración de Internet fijo. Los mayores diferenciales positivos aparecen en **Saavedra**, **Lonquimay**, **Galvarino**, **Alto Biobío** y **Toltén**. Esta medida no es un índice oficial: se utiliza como señal exploratoria para detectar territorios donde la pobreza social convive con baja conectividad fija.

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

La siguiente capa pública está diseñada para incorporar las ocho tablas agregadas del CASEN Digital Master. Los archivos preparados contienen 1 fila nacional, 4 macrozonas, 72 observaciones de rankings regionales, 200 observaciones de rankings comunales, 52 comunas RM, 7 grupos de edad, 112 cruces región×edad y 333 observaciones comunales de pobreza versus Internet fijo.

## Principios de publicación

El repositorio mantiene separadas las unidades de análisis, conserva datos faltantes cuando corresponde y no publica microdatos personales, el Índice de Vulnerabilidad Digital completo, ponderadores propietarios ni modelos comerciales.

## Autor

Sebastian Elgueta Godoy

Sociología, políticas públicas, telecomunicaciones e infraestructura digital.
