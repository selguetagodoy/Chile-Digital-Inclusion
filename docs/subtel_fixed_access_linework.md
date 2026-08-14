# Infraestructura fija pública — SUBTEL RedAcceso

Esta capa utiliza servicios ArcGIS públicos del servidor Licancabur de SUBTEL para describir **presencia de trazados regulatorios publicados de redes de acceso fijo**. No se interpreta automáticamente como cobertura comercial, FTTH disponible para cada hogar ni porcentaje de población cubierta.

## Descubrimiento de fuentes

`scripts/discover_subtel_redacceso_services.py` enumera los servicios públicos cuyo nombre contiene `RedAcceso`. El catálogo de descubrimiento se conserva en `data/fixed_access_infrastructure/service_discovery.csv`.

El catálogo consultable actual identifica seis capas lineales públicas accesibles sin token:

| Entidad | Capa | Registros lineales |
|---|---|---:|
| Claro | RedAcceso_HFC | 23.806 |
| Claro | RedAcceso | 76.217 |
| Entel | RedAcceso_distribucion | 53.654 |
| Entel | RedAcceso_primarias | 9.626 |
| Infraco | RedAcceso | 311.419 |
| VTR | RedAcceso_FTTH | 32.337 |

En conjunto son **507.059 registros lineales consultables** en los servicios públicos procesados.

Los servicios `Of468_CTR_RedAcceso` y `Of468_Mundo_RedAcceso` fueron descubiertos, pero actualmente responden `ArcGIS error 499 / Token Required` en el endpoint FeatureServer. El pipeline los registra y los excluye del procesamiento público. No intenta evadir el control de acceso.

## Por qué no se llama “cobertura de fibra”

Los nombres de las capas son heterogéneos. Algunas identifican explícitamente tecnología o función —por ejemplo `Claro_RedAcceso_HFC` y `VTR_RedAcceso_FTTH`—, mientras otras solo se denominan `RedAcceso`, `distribucion` o `primarias`.

Por eso:

- el nombre `FTTH` se conserva únicamente para la capa que SUBTEL publica con esa denominación;
- el nombre `HFC` se conserva únicamente donde aparece explícitamente en el servicio;
- una capa genérica `RedAcceso` no se reclasifica como fibra por inferencia;
- la presencia de un trazado en una comuna no prueba que todos los hogares puedan contratar un servicio;
- los registros de distintas capas pueden representar trazados superpuestos o funciones de red diferentes.

## Capa canónica de presencia comunal

`scripts/build_subtel_fixed_access_presence.py` consulta los seis servicios públicos accesibles usando cada polígono comunal como filtro espacial ArcGIS.

Se ejecutan **2.076 consultas espaciales** —346 comunas × 6 capas—. El último QA registra:

- 2.076 consultas procesadas;
- cero fallas de consulta;
- 307 comunas con al menos una capa RedAcceso pública observable;
- hasta cuatro operadores/entidades con trazados públicos en una misma comuna.

Antártica permanece en la tabla administrativa de 346 comunas, pero no tiene geometría en la capa BCN usada por el proyecto y por eso sus consultas quedan registradas como `no_commune_geometry`.

Productos canónicos:

- `commune_fixed_access_presence.csv` — 346 comunas con conteos por capa y resúmenes de presencia;
- `presence_query_qa.csv` — una fila por comuna × capa con estado de la consulta.

Los conteos de registros que intersectan una comuna se conservan para auditoría. No se integran como una métrica de “cantidad de red” porque un mismo tramo puede cruzar límites comunales o existir en capas superpuestas.

## Agregación geométrica detallada

`scripts/build_subtel_fixed_access_communes.py` implementa una segunda capa, más costosa, que descarga las geometrías y corta cada tramo por límites comunales. El procedimiento normaliza y repara geometrías, utiliza STRtree para búsqueda espacial, intersecta líneas con polígonos y calcula longitud geodésica del fragmento dentro de cada comuna.

Esta salida se trata como **producto técnico complementario** y no es requisito del maestro público. Su objetivo es auditar densidad y trazado, no producir una tasa de cobertura.

## Campos que entran al maestro comunal

El maestro público incorpora únicamente dos resúmenes de presencia:

- `fixed_access_public_layers_present` — número de capas RedAcceso públicas con al menos un registro que intersecta la comuna;
- `fixed_access_public_operators_present` — número de entidades/operadores con al menos un trazado público que intersecta la comuna.

El detalle por servicio queda en `data/fixed_access_infrastructure/` para evitar convertir el maestro analítico en una matriz técnica excesivamente ancha.

## Interpretación

Esta capa sirve para observar **presencia de infraestructura regulatoria publicada**. Complementa Censo, CASEN, encuestas SUBTEL y Ookla, pero no sustituye:

- cobertura comercial declarada por operador;
- hogares pasados por fibra;
- homes passed / homes connected;
- disponibilidad de un plan en una dirección;
- capacidad efectiva o congestión;
- calidad observada de servicio.

Última revisión: 2026-08-14.
