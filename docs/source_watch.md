# Monitoreo de fuentes oficiales

## Objetivo

El repositorio mantiene un monitor de descubrimiento para detectar nuevas publicaciones o modificaciones en fuentes oficiales que alimentan capas de conectividad digital. El monitor no incorpora cifras nuevas automáticamente al maestro ni reemplaza vintages existentes.

Su función es separar dos etapas:

1. detección automática de que una fuente oficial cambió;
2. revisión humana y actualización controlada del pipeline correspondiente.

## Fuentes monitoreadas

La configuración se encuentra en `config/source_watch.csv` y actualmente cubre:

- informes sectoriales SUBTEL;
- series administrativas de Internet y tráfico SUBTEL;
- informes del Fondo de Desarrollo de las Telecomunicaciones;
- publicaciones SUBTEL asociadas al Organismo Técnico Independiente;
- iniciativas y convocatorias de conectividad del Centro de Innovación Mineduc;
- documentación de Conectividad para la Educación 2030.

Las URLs configuradas son páginas oficiales de descubrimiento o publicación. Se privilegian landing pages estables sobre enlaces temporales a archivos específicos para poder detectar futuras versiones.

## Método

`scripts/watch_official_sources.py` descarga cada página con librerías estándar de Python y construye una huella SHA-256 únicamente sobre elementos relevantes definidos en la configuración.

Existen tres modos:

- `html_links`: normaliza y ordena enlaces cuyo texto o URL contiene alguno de los términos configurados;
- `html_text`: normaliza fragmentos visibles de texto que contienen alguno de los términos configurados;
- `body_hash`: calcula la huella del cuerpo completo y se reserva para recursos donde no existe una estructura HTML útil.

Los acentos se normalizan para evitar diferencias artificiales en los filtros. Las listas se ordenan y deduplican antes de calcular la huella.

## Estado y eventos

El estado persistente se guarda en:

`data/metadata/source_watch_state.csv`

Cuando existe una variación relevante se genera además:

`data/metadata/source_watch_report.csv`

Los eventos posibles incluyen:

- `BASELINE`: primera observación válida;
- `CHANGED`: cambió la huella de elementos relevantes;
- `ERROR`: una fuente previamente válida dejó de ser accesible o procesable;
- `EMPTY`: la página respondió pero ya no contiene ningún elemento que cumpla el contrato configurado;
- `RECOVERED`: una fuente vuelve a responder correctamente después de un error;
- `UNCHANGED`: no existe cambio semántico detectable.

La primera ejecución establece una línea base y no genera una alerta de revisión por el solo hecho de que todas las fuentes sean nuevas para el monitor.

## Automatización

`.github/workflows/watch-official-sources.yml` se ejecuta semanalmente los lunes y también puede iniciarse manualmente.

Cada ejecución:

1. revisa las fuentes configuradas;
2. genera un reporte CSV como artifact de GitHub Actions;
3. actualiza el estado persistente solo cuando existe un cambio de estado o huella;
4. crea un issue cuando una fuente cambia o presenta un problema nuevo;
5. no modifica ninguna capa canónica de datos.

De este modo el historial de Git no recibe commits semanales si las fuentes permanecen iguales.

## Regla de promoción de datos

Una alerta de fuente nunca es evidencia suficiente para modificar el maestro. Antes de incorporar un nuevo valor se debe:

1. abrir y verificar la publicación primaria;
2. identificar fecha de publicación y período estadístico de referencia;
3. confirmar si cambió el universo, metodología, unidad o estructura del archivo;
4. conservar la precisión original y cualquier calificador publicado;
5. mantener separados vintages incompatibles;
6. actualizar el pipeline específico y sus controles QA;
7. validar el release completo antes de considerar la nueva capa consistente.

No se permite interpolar, extrapolar, retroproyectar, calcular puntos medios de rangos ni reemplazar silenciosamente un dato histórico por una revisión posterior.

## Mantenimiento

Agregar una fuente nueva requiere una fila en `config/source_watch.csv` con identificador estable, editor, URL oficial, modo de extracción y términos relevantes. Si una página cambia de estructura y el monitor queda en `EMPTY`, primero debe revisarse el contrato de extracción; no se debe interpretar automáticamente como ausencia de una nueva publicación.

Última revisión: 2026-09-12.
