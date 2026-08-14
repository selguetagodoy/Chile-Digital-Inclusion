from pathlib import Path

README = Path('README.md')
REPRO = Path('docs/reproducibility.md')

SECTOR_BLOCK = '''### Serie administrativa SUBTEL — 2000/2009–marzo 2026

`data/subtel_sector_series/` normaliza los cuatro XLSX oficiales de SUBTEL publicados hasta marzo de 2026: conexiones fijas, conexiones móviles por tecnología, tráfico móvil y tráfico fijo.

La tabla canónica `sector_core_monthly_long.csv` mantiene cada serie en su rango efectivo. El XLSX fijo contiene observaciones desde diciembre de 2000; la tecnología móvil parte en diciembre de 2009; el tráfico móvil en junio de 2017 y el tráfico fijo en enero de 2019. No se interpolan períodos anteriores.

Para tecnología fija no se fuerza una falsa serie histórica: la hoja nacional cambia de taxonomía en el tiempo. El corte actual de marzo de 2026 usa las columnas explícitamente etiquetadas de la hoja vigente y registra **4.147.629 conexiones FTTX/fibra**, equivalentes a **85,35%** de 4.859.679 conexiones fijas.

El XLSX mensual registra **10.356.448 conexiones 5G en marzo de 2026**, mientras el snapshot sectorial Q1 conservado en otra capa oficial informa 10.367.754. La diferencia de 11.306 conexiones se mantiene documentada por procedencia y no se corrige artificialmente.

La metodología, rangos y controles están en `docs/subtel_sector_longitudinal.md`.
'''

REPRO_BLOCK = '''### Series administrativas SUBTEL de conexiones y tráfico

`build-subtel-sector-series-2026.yml` descarga los cuatro XLSX oficiales publicados hasta marzo de 2026 y genera la serie canónica en formato largo.

El pipeline mantiene separados:

- conexiones fijas totales;
- tecnologías móviles 2G/3G/4G/5G;
- tráfico móvil;
- tráfico fijo;
- snapshot tecnológico fijo de marzo de 2026 con etiquetas explícitas.

La hoja histórica nacional de tecnología fija no se trata como una taxonomía homogénea cuando sus columnas cambian. La composición fija actual se toma de `7.7.1.CO_TEC_RG_EMP_FIJAS`, cuyos totales etiquetados reconcilian con las 4.859.679 conexiones fijas de marzo de 2026.

Las discrepancias entre publicaciones oficiales —como los 10.356.448 accesos 5G del XLSX mensual de marzo frente a 10.367.754 en el snapshot sectorial Q1— se conservan con procedencia separada y quedan visibles en `series_qa.csv`.
'''


def insert_before(text: str, marker: str, block: str) -> str:
    if block.strip() in text:
        return text
    if marker not in text:
        raise RuntimeError(f'Marker not found: {marker}')
    return text.replace(marker, block.rstrip() + '\n\n' + marker, 1)


def main():
    readme = README.read_text(encoding='utf-8')
    readme = insert_before(readme, '### OTI — velocidad fija regional, enero 2026', SECTOR_BLOCK)
    readme = readme.replace('documenta **19 capas**, de las cuales **18 son canónicas**', 'documenta **20 capas**, de las cuales **19 son canónicas**')
    if '│   ├── subtel_sector_series/' not in readme:
        readme = readme.replace('│   ├── subtel_sector_2026/\n', '│   ├── subtel_sector_2026/\n│   ├── subtel_sector_series/\n', 1)
    README.write_text(readme, encoding='utf-8')

    repro = REPRO.read_text(encoding='utf-8')
    repro = insert_before(repro, '### Redes móviles SUBTEL 4G/5G', REPRO_BLOCK)
    # Add the layer to the recommended reconstruction order without renumbering unrelated prose manually.
    old = '3. encuestas SUBTEL y productos longitudinales;\n4. Ookla nacional y territorial;'
    new = '3. encuestas SUBTEL y productos longitudinales;\n4. series administrativas SUBTEL de conexiones y tráfico;\n5. Ookla nacional y territorial;'
    if old in repro:
        repro = repro.replace(old, new, 1)
        repro = repro.replace('5. 4G/5G SUBTEL;\n6. RedAcceso SUBTEL;\n7. Mineduc Aulas Conectadas y Directorio RBD;\n8. integraciones al maestro;\n9. diccionario;\n10. dashboard;\n11. `validate-public-release.yml`;\n12. release metadata.', '6. 4G/5G SUBTEL;\n7. RedAcceso SUBTEL;\n8. Mineduc Aulas Conectadas y Directorio RBD;\n9. integraciones al maestro;\n10. diccionario;\n11. dashboard;\n12. `validate-public-release.yml`;\n13. release metadata.', 1)
    REPRO.write_text(repro, encoding='utf-8')
    print('Documentation synchronized with longitudinal SUBTEL sector series')

if __name__ == '__main__':
    main()
