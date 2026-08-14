# SUBTEL — registros de red móvil 4G y 5G por comuna

Esta capa utiliza servicios ArcGIS públicos de SUBTEL correspondientes a marzo de 2025 para Claro, Entel, Movistar y WOM.

## Qué mide

Los servicios exponen geometrías puntuales asociadas a las redes 4G y 5G de cada operador. El repositorio conserva y agrega esos registros como **registros puntuales de red**.

No se interpretan como:

- torres físicas únicas
- porcentaje de territorio cubierto
- porcentaje de población cubierta
- estaciones base únicas sin duplicados

Una misma ubicación física puede contener más de un registro, banda, sistema radiante o capa tecnológica. Por eso el nombre de las variables conserva explícitamente `point_records`.

## Productos

`data/mobile_coverage_2025/service_catalog.csv`

Inventario de los ocho servicios públicos utilizados, con operador, tecnología, tipo de geometría, número de registros y capacidades de consulta.

`data/mobile_coverage_2025/commune_operator_technology_points_2025_03.csv`

Formato largo comuna × operador × tecnología.

`data/mobile_coverage_2025/commune_mobile_network_points_2025_03.csv`

Formato ancho por comuna, con registros 4G y 5G por operador, total de registros por tecnología y número de operadores con al menos un registro dentro de la comuna.

`data/mobile_coverage_2025/spatial_assignment_coverage.csv`

Control de asignación espacial por operador y tecnología.

## Método espacial

1. Se consulta el identificador de cada entidad en los servicios ArcGIS públicos.
2. Los registros se descargan con geometría y se reproyectan mediante la API a WGS84.
3. Cada punto se asigna al polígono comunal de la capa BCN utilizada por el proyecto.
4. Se cuenta el número de registros por comuna, operador y tecnología.
5. Las 346 comunas permanecen en la tabla final; cuando no existe un registro asignado, el conteo es cero.

La comuna de Antártica permanece en el catálogo estadístico aunque la capa comunal BCN usada en el dashboard no contiene su geometría. No se inventa una geometría para completar ese vacío.

## Uso analítico

La capa permite estudiar presencia y concentración territorial de infraestructura móvil observable, complementar los indicadores de acceso del Censo/CASEN/SUBTEL y contrastarlos con desempeño Ookla.

El número de operadores con registros 5G en una comuna puede utilizarse como una medida descriptiva de presencia de redes, pero no debe llamarse cobertura efectiva sin un cálculo adicional de superficie o población cubierta.

## Fuente

Portal de mapas y servicios ArcGIS públicos de la Subsecretaría de Telecomunicaciones. Los endpoints exactos utilizados quedan registrados en `service_catalog.csv`.

Última revisión: 2026-08-14.
