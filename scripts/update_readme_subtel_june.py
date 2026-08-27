from pathlib import Path

README = Path('README.md')
text = README.read_text(encoding='utf-8')

q_start = text.index('### SUBTEL — contexto sectorial Q1 2026')
q_end = text.index('### Redes móviles 4G/5G — SUBTEL marzo 2025')
q_block = '''### SUBTEL — contexto sectorial 1S 2026

`data/subtel_sector_2026/sector_snapshot_2026q1.csv` conserva el cierre sectorial de marzo de 2026 y `data/subtel_sector_2026/sector_snapshot_2026q2.csv` incorpora el cierre de junio de 2026 publicado por SUBTEL.

A junio de 2026 el snapshot oficial registra **4.900.369 accesos de Internet fijo**, **10.818.497 conexiones 5G**, **11,446 millones de conexiones 4G** y una brecha 4G–5G de **627.503 conexiones**. La fibra óptica representa **87,3%** de las conexiones fijas.

La penetración sectorial estimada de Internet fijo alcanza **70,36% de los hogares**, con **77,3% urbano** y **25,5% rural**. Esta medida usa conexiones residenciales y hogares del Censo 2024; permanece separada de las estimaciones de acceso provenientes de encuestas de hogares.

El tráfico acumulado de doce meses llega a **37,1211 EB fijo** y **7,7593 EB móvil**. Los snapshots, fuentes y discrepancias editoriales están documentados en `docs/subtel_sector_snapshot_2026q2.md`.

'''
text = text[:q_start] + q_block + text[q_end:]

s_start = text.index('### Serie administrativa SUBTEL — 2000/2009–marzo 2026')
s_end = text.index('### OTI — velocidad fija regional, enero 2026')
s_block = '''### Serie administrativa SUBTEL — 2000/2009–junio 2026

`data/subtel_sector_series/` normaliza los cuatro XLSX oficiales de SUBTEL con cierre en **junio de 2026**: conexiones fijas, conexiones móviles por tecnología, tráfico móvil y tráfico fijo.

La tabla canónica `sector_core_monthly_long.csv` conserva el rango efectivo de cada fuente. Las conexiones fijas contienen observaciones desde diciembre de 2000; la tecnología móvil desde diciembre de 2009; el tráfico móvil desde junio de 2017 y el tráfico fijo desde enero de 2019. No se interpolan períodos anteriores.

El corte mensual de junio de 2026 registra **4.900.369 conexiones fijas**, **22.620.235 conexiones móviles totales**, **11.446.039 conexiones 4G** y **10.818.497 conexiones 5G**. La hoja tecnológica fija registra **4.275.932 conexiones FTTX/fibra**, equivalentes a **87,257%** del total.

La hoja fija contiene cierres anuales de diciembre que se solapan con la serie mensual desde 2010. El pipeline elimina ese doble registro y conserva una sola observación por período: el QA final registra **208 filas y 208 períodos únicos** para conexiones fijas.

Los workbooks más recientes pueden revisar cifras previamente publicadas. El repositorio trata el XLSX vigente como vintage canónico para la serie longitudinal y conserva los snapshots históricos con su cifra original y procedencia. La metodología y los controles están en `docs/subtel_sector_longitudinal.md` y `data/subtel_sector_series/series_qa.csv`.

'''
text = text[:s_start] + s_block + text[s_end:]

text = text.replace(
    'También muestra un contexto sectorial nacional actualizado a marzo de 2026.',
    'También muestra un contexto sectorial nacional con fuentes actualizadas hasta junio de 2026.'
)
text = text.replace(
    '- snapshot sectorial SUBTEL Q1 2026',
    '- snapshots sectoriales SUBTEL Q1 y Q2 2026'
)

README.write_text(text, encoding='utf-8')
print('README SUBTEL sections updated through June 2026')
