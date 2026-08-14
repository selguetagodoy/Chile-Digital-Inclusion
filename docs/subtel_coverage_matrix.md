# Cobertura de datos SUBTEL

Este repositorio distingue tres niveles de procesamiento: series longitudinales curadas, perfiles masivos de las bases oficiales y tabulados segmentados validados. Una ola no se considera comparable solo porque exista la misma palabra en dos cuestionarios.

## Serie curada de acceso y uso

| Dimensión | 2015 | 2016 | 2017 | 2023 | 2024 | 2025 | Estado |
|---|---|---|---|---|---|---|---|
| Acceso pagado del hogar | Sí | Sí | Sí | Sí | Sí | Sí | Armonizado |
| Fijo / móvil / fijo+móvil | Sí | Sí | Sí | Sí | Sí | Sí | Armonizado |
| Urbano / rural | Sí | Sí | Sí | Sí | Sí | Sí | Armonizado con notas |
| Dispositivos del hogar | Sí | Sí | Sí | Sí | Sí | Sí | Armonizado con cambios de categorías |
| Frecuencia de uso | Sí | Sí | Parcial | Sí | Sí | Sí | Quiebre de ventana desde 2024 |
| Hogares solo de personas mayores | No | No | Sí | Sí | Sí | Sí | Serie descriptiva |
| Habilidades digitales | No | No | No | Sí | Sí | Sí | Serie comparable reciente |
| Habilidades por edad | No | No | No | No | No | Sí | Disponible 2025 |
| Teletrabajo por edad | No | No | No | No | No | Sí | Disponible 2025 |
| E-learning por edad | No | No | No | No | No | Sí | Disponible 2025 |
| Estado digital por sexo | No | No | No | No | No | Sí | Disponible 2025 |
| Seguridad digital | No | No | No | No | Parcial | Parcial | Variables identificadas; armonización temática pendiente |
| IA | No aplica | No aplica | No aplica | No | Sí | Sí | Ítem introducido en 2024 |

## Acceso segmentado validado

`data/subtel_segments/` publica **127 tabulados agregados** construidos directamente desde los SAV oficiales para las olas 2015, 2016, 2017, 2023, 2024 y 2025.

| Segmentación del acceso pagado del hogar | 2015 | 2016 | 2017 | 2023 | 2024 | 2025 | Estado |
|---|---|---|---|---|---|---|---|
| Nacional | Sí | Sí | Sí | Sí | Sí | Sí | Ponderado y validado |
| Región | Sí | Sí | Sí | Sí | Sí | Sí | Ponderado por factor de hogar |
| Urbano / rural | Sí | Sí | Sí | Sí | Sí | Sí | Ponderado por factor de hogar |
| Quintil / GSE explícito | Sí | Sí | Sí | No | No | No | Solo cuando la base trae categoría explícita verificable |

El control nacional recalculado reproduce la serie publicada con diferencias de -0,31 pp en 2015, -0,002 pp en 2016, -0,001 pp en 2017, +0,047 pp en 2023, +0,0004 pp en 2024 y -0,035 pp en 2025.

Para 2023–2025 no se encontró una variable explícita de quintil/GSE con hasta diez categorías que cumpliera la regla conservadora del pipeline. No se reconstruyen quintiles desde tramos de ingreso ni se fuerza una equivalencia socioeconómica.

## Perfiles masivos de las bases oficiales

`data/subtel_microdata/` y `data/subtel_weighted/` procesan las bases oficiales disponibles entre 2011 y 2025, además de una capa histórica 2008. El pipeline inventaría miles de variables, clasifica dominios temáticos y publica distribuciones agregadas con ponderadores de hogar y persona separados cuando existen.

Los dominios localizados incluyen:

- acceso y tipo de conexión
- región, comuna y urbano/rural
- edad y sexo
- ingreso y GSE
- dispositivos
- barreras de adopción y no adopción
- banca, pagos y comercio electrónico
- trámites y Estado digital
- educación, empleo y teletrabajo
- habilidades digitales
- seguridad, privacidad y fraude
- discapacidad
- pueblos originarios
- calidad y satisfacción percibida

La clasificación automática sirve para encontrar preguntas candidatas. No convierte por sí sola dos variables en una serie longitudinal.

## Brechas que siguen abiertas

El núcleo de acceso territorial está cerrado para las seis olas principales. Lo que permanece abierto corresponde a armonizaciones temáticas más exigentes, no a falta de extracción de microdatos:

1. uso de Internet por edad y sexo con definición homogénea de usuario
2. banca, pagos y Estado digital en series largas
3. seguridad, privacidad, fraude y percepción de protección
4. calidad y satisfacción percibida
5. módulos especiales de personas mayores
6. pueblos originarios, manteniendo el universo específico de cada módulo
7. barreras de no adopción con categorías comparables entre cuestionarios
8. una clasificación socioeconómica armonizada posterior a 2017, solo si la documentación oficial permite equivalencia defendible

## Regla de publicación

Las bases SAV oficiales se descargan durante GitHub Actions y no se almacenan como microdatos en el repositorio. Se publican tabulados agregados y se suprimen celdas con menos de 30 observaciones sin ponderar.

Una variable entra en una serie longitudinal solo cuando pregunta, universo, período de recuerdo y categorías son suficientemente comparables. En caso contrario se conserva como evidencia de una ola específica.

Última revisión: 2026-08-13.
