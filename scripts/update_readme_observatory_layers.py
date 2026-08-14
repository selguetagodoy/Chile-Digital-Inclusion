from pathlib import Path

README = Path('README.md')


def insert_before(text: str, marker: str, block: str) -> str:
    if block.strip() in text:
        return text
    if marker not in text:
        raise RuntimeError(f'Marker not found: {marker}')
    return text.replace(marker, block.rstrip() + '\n\n' + marker, 1)


def main():
    text = README.read_text(encoding='utf-8')

    text = text.replace(
        'Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de Censo 2024, CASEN 2024, Encuestas de Acceso y Usos de Internet de SUBTEL, estadísticas sectoriales, registros públicos de redes móviles y calidad observada de red.',
        'Repositorio abierto para analizar inclusión, exclusión y desigualdad digital en Chile a partir de Censo 2024, CASEN 2024, Encuestas de Acceso y Usos de Internet de SUBTEL, estadísticas sectoriales, registros públicos de redes móviles y fijas, conectividad educativa y calidad observada de red.'
    )
    text = text.replace(
        'La versión pública combina evidencia censal, encuestas sociales y de telecomunicaciones, estadísticas sectoriales, registros públicos 4G/5G, desempeño observado de red, cartografía comunal y pipelines reproducibles.',
        'La versión pública combina evidencia censal, encuestas sociales y de telecomunicaciones, estadísticas sectoriales, registros públicos 4G/5G, trazados RedAcceso, programas de conectividad educativa, desempeño observado de red, cartografía comunal y pipelines reproducibles.'
    )

    old_master = '`data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv` agrega desempeño Ookla fijo y móvil Q1 2026, variaciones Q4 2025 → Q1 2026 y registros públicos SUBTEL 4G/5G de marzo de 2025 por operador. Conserva las **346 comunas y contiene 77 variables**.'
    new_master = '`data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv` agrega desempeño Ookla fijo y móvil Q1 2026, variaciones Q4 2025 → Q1 2026, registros públicos SUBTEL 4G/5G de marzo de 2025, presencia de capas públicas RedAcceso y Aulas Conectadas 2025 territorializado por RBD. Conserva las **346 comunas y contiene 84 variables**.'
    if old_master in text:
        text = text.replace(old_master, new_master, 1)
    else:
        text = text.replace('**346 comunas y contiene 77 variables**', '**346 comunas y contiene 84 variables**')

    fixed_block = '''### Infraestructura fija pública — SUBTEL RedAcceso

`data/fixed_access_infrastructure/` inventaría los servicios públicos `RedAcceso` del servidor ArcGIS de SUBTEL. El catálogo actual identifica seis capas lineales accesibles sin token, correspondientes a Claro, Entel, Infraco y VTR, con **507.059 registros lineales consultables** en conjunto.

La capa de presencia comunal ejecuta **2.076 consultas espaciales** —346 comunas × 6 capas— sin fallas y detecta **307 comunas con al menos una capa RedAcceso pública**. El máximo observado es cuatro operadores/entidades presentes en una comuna.

El maestro integrado incorpora solo dos campos robustos: número de capas públicas presentes y número de operadores/entidades presentes. Los conteos por servicio quedan en la carpeta técnica.

`RedAcceso` no se interpreta como porcentaje de cobertura, hogares pasados por fibra ni disponibilidad comercial en una dirección. Los servicios `Of468_CTR_RedAcceso` y `Of468_Mundo_RedAcceso` fueron descubiertos pero actualmente exigen token; quedan registrados y excluidos, sin intentar eludir ese control de acceso.

La metodología y la frontera de interpretación están en `docs/subtel_fixed_access_linework.md`.
'''

    education_block = '''### Conectividad educativa — Mineduc 2025/2026

`data/education_connectivity_2026/` incorpora programas y registros administrativos oficiales de conectividad e infraestructura digital educativa.

Para Aulas Conectadas 2025 se procesa la planilla oficial de Mineduc con **793 RBD únicos**: **700 establecimientos seleccionados** y **93 en lista de espera**. Los RBD se cruzan exclusivamente con el Directorio Oficial de Establecimientos Educacionales 2025, que contiene 16.768 establecimientos de datos.

El cruce logra **793 de 793 RBD, equivalente a 100% de match**, sin duplicados ni establecimientos sin resolver. Los 700 seleccionados se distribuyen en **196 comunas**. El resumen comunal mantiene seleccionados, lista de espera, seleccionados rurales, matrícula administrativa de los establecimientos y disponibilidad de coordenadas.

La selección en un programa no equivale a conectividad ya instalada ni a acceso domiciliario de los estudiantes. La suma de matrícula describe el tamaño de los establecimientos seleccionados y no el número de estudiantes efectivamente beneficiados.

La metodología completa está en `docs/education_connectivity_2026.md`.
'''

    marker = '### SUBTEL — procesamiento de bases oficiales'
    text = insert_before(text, marker, fixed_block)
    text = insert_before(text, marker, education_block)

    text = text.replace(
        'La vista carga el maestro comunal integrado y el GeoJSON. Permite cambiar indicador, buscar comunas, revisar rankings y abrir una ficha territorial con conectividad, equipamiento, contexto social, registros 4G/5G y desempeño Ookla. También muestra un contexto sectorial nacional actualizado a marzo de 2026.',
        'La vista carga el maestro comunal integrado y el GeoJSON. Permite cambiar indicador, buscar comunas, revisar rankings y abrir una ficha territorial con conectividad, equipamiento, contexto social, registros 4G/5G, presencia RedAcceso, Aulas Conectadas y desempeño Ookla. También muestra un contexto sectorial nacional actualizado a marzo de 2026.'
    )

    text = text.replace(
        '│   ├── mobile_coverage_2025/\n│   ├── subtel_sector_2026/',
        '│   ├── mobile_coverage_2025/\n│   ├── fixed_access_infrastructure/\n│   ├── education_connectivity_2026/\n│   ├── subtel_sector_2026/'
    )

    text = text.replace(
        '- integración de infraestructura móvil al maestro comunal\n- descarga y control trimestral Ookla',
        '- integración de infraestructura móvil al maestro comunal\n- descubrimiento, catálogo y presencia comunal de capas RedAcceso SUBTEL\n- descarga y normalización de Aulas Conectadas 2025\n- crosswalk oficial RBD → comuna mediante el Directorio Mineduc 2025\n- integración educativa al maestro comunal\n- descarga y control trimestral Ookla'
    )

    source_marker = '- Subsecretaría de Telecomunicaciones — Encuestas de Acceso y Usos de Internet y estadísticas sectoriales'
    if source_marker in text and '- Ministerio de Educación — Aulas Conectadas' not in text:
        text = text.replace(source_marker, source_marker + '\n- Ministerio de Educación — Aulas Conectadas, CpE2030 y Directorio Oficial de Establecimientos Educacionales 2025', 1)

    README.write_text(text, encoding='utf-8')
    print('README updated for 84-variable integrated master')

if __name__ == '__main__':
    main()
