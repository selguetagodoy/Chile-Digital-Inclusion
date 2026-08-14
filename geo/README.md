# Geografía comunal

Esta carpeta estandariza la llave territorial utilizada por Chile Digital Inclusion.

## Archivos

### `commune_codes.csv`

Tabla de referencia con las 346 comunas, sus códigos y la jerarquía región–provincia–comuna.

### `chile_communes.geojson`

Cartografía comunal ligera en WGS84 generada automáticamente desde la capa pública `División Comunal` de la Biblioteca del Congreso Nacional de Chile. Se conservan solamente código de comuna, nombre de comuna, provincia, región y código de región.

Fuente cartográfica:

https://arcgiswebad.bcn.cl/arcgis/rest/services/Hosted/Capa_Factores/FeatureServer/0

La capa BCN utilizada por el pipeline devuelve actualmente 345 polígonos. `geometry_coverage.csv` muestra la diferencia frente al catálogo administrativo de 346 comunas. La comuna de Antártica, código 12202, está en la tabla de códigos y en los datos comunales, pero no tiene polígono en esta capa cartográfica. No se inventa una geometría para completar el archivo.

### `geometry_coverage.csv`

Control de cobertura con una fila por comuna y la variable `has_polygon`.

## Reproducibilidad

`scripts/build_commune_geo.py` consulta el servicio de la BCN, transforma la geometría a EPSG:4326, reduce la precisión para mantener un GeoJSON liviano y genera el control de cobertura. El workflow `build-commune-geo.yml` reconstruye el archivo automáticamente.

Última revisión: 2026-08-13.
