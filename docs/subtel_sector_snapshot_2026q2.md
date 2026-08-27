# SUBTEL — contexto sectorial Q2 / primer semestre 2026

## Alcance

`data/subtel_sector_2026/sector_snapshot_2026q2.csv` consolida indicadores sectoriales oficiales con cierre a junio de 2026 publicados por la Subsecretaría de Telecomunicaciones de Chile (SUBTEL). El archivo mantiene la misma lógica de trazabilidad utilizada para Q1 2026: periodo, indicador, valor, unidad, tipo estadístico, universo o base, página fuente, URL y nota metodológica.

La fuente canónica del snapshot es el **Informe Semestral del Sector Telecomunicaciones – Primer Semestre 2026**. Las cuatro planillas XLSX de series oficiales actualizadas a junio de 2026 quedan registradas en `source_catalog_2026q2.csv` como fuentes longitudinales para ETL y reconstrucción mensual.

## Principales indicadores a junio de 2026

- Internet fijo: **4.900.369 accesos**, +3,3% interanual.
- Internet móvil 3G+4G+5G: **22,591 millones de accesos**, -0,4% interanual.
- 5G: **10.818.497 accesos**, +31,8% interanual.
- 4G: **11,446 millones de accesos**, -16,8% interanual.
- Brecha 4G–5G: **627.503 conexiones**.
- Fibra óptica: **87,3%** de las conexiones fijas; crecimiento interanual de 20,7%.
- Penetración estimada de Internet fijo en hogares: **70,36% nacional**, **77,3% urbana** y **25,5% rural**.
- Tráfico acumulado 12 meses: **37,1211 EB fijo** y **7,7593 EB móvil**.
- Tráfico mensual medio por conexión informado por SUBTEL: **699,4 GB fijo** y **30,8 GB móvil**.
- M2M móvil: **500.464 accesos**, equivalentes a 2,2% del universo 3G+4G+5G.

## Fronteras de interpretación

La penetración fija de hogares es una **estimación sectorial**, calculada a partir de conexiones residenciales y del número de hogares del Censo 2024. Debe mantenerse separada de los indicadores de acceso provenientes de encuestas de hogares, porque miden universos y conceptos distintos.

Los conteos de servicios y conexiones tampoco representan personas únicas. Una persona u hogar puede mantener múltiples servicios o accesos.

## QA y discrepancias editoriales detectadas

### Participación de operadores en fibra óptica

El PDF semestral es la fuente canónica. Para junio de 2026 reporta la siguiente distribución de conexiones de fibra óptica: Movistar 30,4%; Mundo Pacífico 24,3%; Claro-VTR 19,6%; Entel 12,5%; GTD 6,9%; WOM 5,1%; otros 1,3%.

La nota de prensa publicada por SUBTEL el 27 de agosto de 2026 presenta una transcripción tabular que parece desplazada o incompleta para esta métrica. Por esa razón el repositorio utiliza el cuadro del PDF y documenta la diferencia en vez de reconciliarla mediante inferencia.

### Penetración de telefonía móvil

El informe contiene una inconsistencia interna para la penetración de telefonía móvil por 100 habitantes: una parte del documento muestra **117,7**, mientras otra referencia textual consigna **119,1**. Esta variable queda fuera del snapshot Q2 hasta que exista una serie oficial inequívoca que permita reconciliar el valor.

### Referencias históricas dentro del informe

Algunas láminas contienen cifras de cierre 2025 como contexto narrativo, mientras las tablas sectoriales posteriores muestran el corte vigente de junio de 2026. Para cada indicador se utiliza el bloque que identifica explícitamente junio de 2026 y se conserva la página fuente.

## Regla de precedencia

1. Serie XLSX oficial para reconstrucción longitudinal cuando el campo y el periodo estén identificados de forma inequívoca.
2. PDF sectorial oficial para el snapshot semestral, definiciones y participaciones de mercado.
3. Nota de prensa oficial para cifras de titular o valores adicionales explícitos, como la brecha exacta entre 4G y 5G.
4. Ante una discrepancia, el dato queda documentado como conflicto y no se fuerza una armonización.

## Fuentes

- SUBTEL. *Informe Semestral del Sector Telecomunicaciones – Primer Semestre 2026*. https://www.subtel.gob.cl/wp-content/uploads/2026/08/Informe-del-Sector-Telecomunicaciones-Jun26.pdf
- SUBTEL. *Estadísticas 1° semestre: el 5G avanza a paso firme para alcanzar al 4G y brecha se reduce a solo 627 mil conexiones*. 27 de agosto de 2026. https://www.subtel.gob.cl/estadisticas-1o-semestre-subtel-el-5g-avanza-a-paso-firme-para-alcanzar-al-4g-y-brecha-se-reduce-a-solo-627-mil-conexiones/
- SUBTEL. *Estudios y estadísticas — Internet*. Series oficiales actualizadas a junio de 2026. https://www.subtel.gob.cl/estudios-y-estadisticas/
