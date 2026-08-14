# Infraestructura fija pública — SUBTEL RedAcceso

Esta capa utiliza servicios ArcGIS públicos del servidor Licancabur de SUBTEL para describir **trazados regulatorios publicados de redes de acceso fijo**. No se interpreta automáticamente como cobertura comercial, FTTH disponible para cada hogar ni porcentaje de población cubierta.

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
- la suma de kilómetros entre capas puede contener superposición física entre trazados o funciones de red.

## Agregación comunal

`scripts/build_subtel_fixed_access_communes.py` descarga los registros lineales de las capas públicas consultables y los cruza con `geo/chile_communes.geojson`.

El procedimiento:

1. normaliza cada geometría lineal a WGS84;
2. repara geometrías inválidas cuando es posible;
3. conserva exclusivamente componentes poligonales para límites comunales y componentes lineales para redes;
4. busca candidatos mediante un índice espacial STRtree;
5. intersecta el tramo con cada polígono comunal;
6. corta los trazados que atraviesan más de una comuna;
7. calcula longitud geodésica del fragmento dentro de cada comuna;
8. registra fallos topológicos residuales en QA en vez de asignar geometrías dudosas.

Esto evita asignar un tramo completo a una sola comuna solo porque su centroide o primer vértice cae allí.

## Productos

- `service_discovery.csv` — inventario dinámico de servicios RedAcceso encontrados.
- `service_catalog.csv` — capas procesables, geometría, estado y conteo de registros.
- `field_catalog.csv` — diccionario técnico de campos expuestos por los servicios.
- `attribute_profile.csv` — perfil de atributos seleccionados para auditoría.
- `commune_operator_linework.csv` — agregación comuna × capa/entidad.
- `commune_fixed_access_linework.csv` — tabla ancha de 346 comunas.
- `spatial_assignment_coverage.csv` — QA de segmentos y longitud asignada por capa.

## Campos que entran al maestro comunal

El maestro público incorpora únicamente tres resúmenes robustos:

- `fixed_access_public_linework_length_km` — suma de longitud de trazados públicos procesados dentro de la comuna; puede incluir superposición entre capas.
- `fixed_access_public_layers_present` — número de capas RedAcceso públicas con al menos un tramo en la comuna.
- `fixed_access_public_operators_present` — número de entidades/operadores con al menos un trazado público en la comuna.

El detalle por servicio queda fuera del maestro para evitar convertir una base analítica en una matriz técnica excesivamente ancha.

## Interpretación

Esta capa sirve para observar **presencia y densidad de trazado regulatorio publicado**. Complementa Censo, CASEN, encuestas SUBTEL y Ookla, pero no sustituye:

- cobertura comercial declarada por operador;
- hogares pasados por fibra;
- homes passed / homes connected;
- disponibilidad de un plan en una dirección;
- capacidad efectiva o congestión;
- calidad observada de servicio.

Última revisión: 2026-08-14.
