from pathlib import Path

p = Path('README.md')
text = p.read_text(encoding='utf-8')

text = text.replace(
    'conexiones fijas administrativas SUBTEL a marzo de 2026.',
    'conexiones fijas administrativas SUBTEL a junio de 2026.'
)

start_marker = '### Conexiones fijas por comuna — SUBTEL marzo 2026'
end_marker = '### Infraestructura fija pública — SUBTEL RedAcceso'
if start_marker in text and end_marker in text:
    start = text.index(start_marker)
    end = text.index(end_marker)
    block = '''### Conexiones fijas por comuna — SUBTEL junio 2026

`data/fixed_infrastructure_2026/` conserva el corte histórico de marzo y agrega el corte comunal vigente de **junio de 2026** desde las hojas oficiales `7.11.CO_FIJAS_COMUNA` y `7.11.1.CO_FIJAS_RES_COMUNA` del workbook SUBTEL actualizado a junio.

La reconstrucción mantiene la regla validada de bloques regionales definidos por fórmulas de subtotal. Para junio, las **32 verificaciones regionales** —16 regiones × conexiones totales/residenciales— concilian con delta cero. Se recuperan valores numéricos para **345 de 346 comunas**; Antártica (12202) continúa explícitamente vacía en la fuente y se conserva como `source_blank`.

El corte comunal suma exactamente **4.900.369 conexiones fijas**, igual al total nacional oficial de junio de 2026. El archivo principal es `data/fixed_infrastructure_2026/commune_fixed_connections_2026_06.csv`; la trazabilidad incluye `source_alignment_qa_2026_06.csv`, `source_row_mapping_2026_06.csv` y `extraction_manifest_2026_06.csv`.

El maestro integrado conserva simultáneamente los campos de marzo y agrega cinco campos `2026m06`: conexiones fijas totales, residenciales, participación residencial, intensidad residencial por 100 hogares del Censo 2024 y estado de fuente. La intensidad por 100 hogares es un indicador administrativo descriptivo y no una tasa de cobertura.

'''
    text = text[:start] + block + text[end:]

p.write_text(text, encoding='utf-8')
print('README commune fixed layer aligned to June 2026')
