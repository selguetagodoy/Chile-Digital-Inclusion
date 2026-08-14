# Reproducibilidad y arquitectura de datos

Chile Digital Inclusion está organizado como un conjunto de capas independientes que convergen en un maestro comunal público. La reproducibilidad no depende de conservar copias privadas de las fuentes: cuando es posible, los workflows descargan las fuentes oficiales durante la ejecución, generan productos agregados y conservan la trazabilidad metodológica.

## Contrato principal

El producto analítico canónico es:

`data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv`

Una fila representa una comuna. El código comunal es la llave territorial principal.

El maestro mantiene separados los universos estadísticos. Que dos variables aparezcan en una misma fila comunal no significa que tengan el mismo denominador, diseño muestral o interpretación causal.

El diccionario canónico es:

`data/metadata/communal_master_dictionary.csv`

Antes de usar una variable deben revisarse `source_layer`, `statistical_unit`, `unit`, `denominator_or_weight` y `comparability_note`.

## Flujo de construcción

```text
Fuentes oficiales y abiertas
        │
        ├── INE / Censo 2024 ────────────────┐
        ├── MDSF / CASEN 2024 ───────────────┤
        ├── SUBTEL encuestas SAV ────────────┤
        ├── SUBTEL estadísticas sectoriales ─┤
        ├── SUBTEL ArcGIS 4G/5G ─────────────┤
        ├── SUBTEL ArcGIS RedAcceso ─────────┤
        ├── Mineduc Aulas + Directorio RBD ──┤
        ├── Ookla Open Data ─────────────────┤
        └── BCN cartografía comunal ─────────┤
                                             │
                                             ▼
                                  productos agregados por capa
                                             │
                                             ▼
                                  controles QA / crosswalks
                                             │
                                             ▼
                                  maestro comunal integrado
                                             │
                        ┌────────────────────┼────────────────────┐
                        ▼                    ▼                    ▼
                   diccionario          dashboard           release metadata
```

## Capas y pipelines

### Geografía

`build-commune-geo.yml`

Reconstruye el catálogo territorial y la cartografía comunal utilizada para joins espaciales. La capa BCN usada en esta versión contiene 345 polígonos; Antártica permanece en la tabla administrativa de 346 comunas y se documenta como ausencia de geometría en la fuente cartográfica utilizada.

### Ookla Open Data

`build-ookla-chile-q1-2026.yml`

Descarga los Parquet oficiales de Ookla Open Data, recorta Chile y genera la capa nacional Q1 2026 junto con el control Q4 2025.

`build-ookla-territorial.yml`

Asigna tiles a comunas y regiones mediante el centroide del tile dentro del polígono BCN y genera los productos territoriales. Los promedios de desempeño se ponderan por número de tests del tile.

Los datos derivados de Ookla conservan los términos CC BY-NC-SA 4.0 de la fuente.

### Encuestas SUBTEL

`profile-subtel-microdata.yml` y workflows históricos relacionados descargan temporalmente las bases SAV oficiales, inventarían variables y publican exclusivamente agregados y metadata.

`build-subtel-segmented-access.yml` genera estimaciones ponderadas de acceso por región, zona urbano/rural y grupo socioeconómico cuando existe una categoría explícita verificable.

`build-subtel-affordability.yml` reconstruye disposición declarada a pagar y barreras de costo. No genera precios comerciales ni una tasa de esfuerzo artificial.

Los SAV originales no se almacenan en el repositorio.

### Redes móviles SUBTEL 4G/5G

`catalog-subtel-mobile-coverage.yml` identifica los ocho servicios públicos de Claro, Entel, Movistar y WOM.

`build-subtel-mobile-coverage-communes.yml` descarga los registros puntuales y los asigna espacialmente a comunas.

Los conteos representan registros publicados por SUBTEL. No son torres únicas ni porcentaje de cobertura geográfica o poblacional.

### Infraestructura fija SUBTEL RedAcceso

`discover-subtel-redacceso-services.yml` enumera dinámicamente los servicios públicos con `RedAcceso` en el servidor ArcGIS.

`catalog-subtel-fixed-access.yml` inspecciona los servicios y conserva su estado, geometría, campos y número de registros.

`build-subtel-fixed-access-presence.yml` ejecuta consultas espaciales comuna × capa y genera la capa canónica de presencia. Esta capa es la que entra al maestro mediante `integrate-fixed-access-presence.yml`.

`build-subtel-fixed-access-communes.yml` implementa un procesamiento geométrico más costoso que corta los trazados por límites comunales y calcula longitud geodésica. Es una auditoría técnica complementaria y no una dependencia del maestro.

Las capas que requieren token se registran como no accesibles y se excluyen. El pipeline no intenta evadir controles de acceso.

### Conectividad educativa Mineduc

La planilla oficial de Aulas Conectadas 2025 se normaliza por RBD.

El Directorio Oficial de Establecimientos Educacionales 2025 se descarga desde Datos Abiertos Mineduc y se utiliza como crosswalk RBD → región → comuna → ruralidad → coordenadas → matrícula.

`build-mineduc-aulas-communal-2025.yml` exige match completo y genera la capa comunal.

`integrate-education-communal.yml` incorpora cinco variables descriptivas al maestro y reconstruye su diccionario.

No se usa OCR para reconstruir listas de establecimientos cuando existe una fuente administrativa estructurada.

### Maestro y metadata

`build-communal-dictionary.yml` reconstruye el diccionario de variables del maestro.

`validate-public-release.yml` verifica integridad estructural, llaves, conteos, QA espacial, crosswalk educativo y contrato del dashboard. Un release con checks fallidos no debe considerarse una versión consistente.

`build-release-metadata.yml` genera:

- `data/metadata/layer_catalog.csv` — catálogo de capas canónicas y de auditoría;
- `data/metadata/release_manifest.csv` — inventario de archivos públicos con tamaño, dimensiones CSV y SHA-256.

Los propios archivos autogenerados de release metadata se excluyen del manifest para evitar checksums autorreferentes y ejecuciones recursivas.

## Orden recomendado de reconstrucción

Para una reconstrucción completa desde fuentes externas, usar este orden lógico:

1. cartografía y códigos comunales;
2. Censo/CASEN y capas base ya publicadas;
3. encuestas SUBTEL y productos longitudinales;
4. Ookla nacional y territorial;
5. 4G/5G SUBTEL;
6. RedAcceso SUBTEL;
7. Mineduc Aulas Conectadas y Directorio RBD;
8. integraciones al maestro;
9. diccionario;
10. dashboard;
11. `validate-public-release.yml`;
12. release metadata.

Los workflows están diseñados para poder ejecutarse por capa. No es necesario reconstruir todo el repositorio para actualizar una sola fuente.

## Reglas de comparabilidad

- Censo trabaja principalmente con hogares y sirve como referencia estructural territorial.
- CASEN utiliza personas ponderadas y no debe transformarse mecánicamente en una tasa censal comunal.
- SUBTEL contiene universos de hogar y persona dentro de sus encuestas; cada estimación usa su ponderador correspondiente.
- Estadísticas sectoriales SUBTEL trabajan con conexiones y estimaciones administrativas.
- Ookla representa tests observados, no una muestra probabilística de hogares.
- 4G/5G SUBTEL representa registros puntuales publicados de red.
- RedAcceso representa trazados regulatorios publicados, no disponibilidad comercial universal.
- Aulas Conectadas representa selección administrativa de establecimientos, no conectividad domiciliaria ni necesariamente obra ya ejecutada.

## Datos que deliberadamente no se publican

La versión pública no contiene:

- microdatos originales SAV de SUBTEL;
- identificadores personales o administrativos innecesarios;
- respuestas abiertas potencialmente sensibles;
- Índice de Vulnerabilidad Digital completo;
- ponderadores propietarios;
- scores internos;
- segmentaciones comerciales;
- modelos o metodología propietaria de consultoría.

## Control de integridad

`data/metadata/public_release_validation.csv` es el resultado visible de la última validación automática.

`data/metadata/release_manifest.csv` permite verificar que un archivo concreto corresponde exactamente a una versión mediante su SHA-256.

`CITATION.cff` entrega la metadata de citación del repositorio. Las licencias y atribuciones de las fuentes originales siguen aplicándose a sus respectivas capas.

Última revisión: 2026-08-14.
