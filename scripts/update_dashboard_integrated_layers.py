from pathlib import Path
import re

JS = Path('assets/dashboard.js')
HTML = Path('index.html')


def replace_once(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f'Expected dashboard marker not found: {old[:80]}')
    return text.replace(old, new, 1)


def main():
    js = JS.read_text(encoding='utf-8')

    js = replace_once(
        js,
        "  mobile_4g_point_records_2025m03: { label: 'Registros de red 4G · mar 2025', unit: '', digits: 0, higherConcern: false },",
        "  mobile_4g_point_records_2025m03: { label: 'Registros de red 4G · mar 2025', unit: '', digits: 0, higherConcern: false },\n  fixed_access_public_operators_present: { label: 'Operadores con trazado RedAcceso público', unit: '', digits: 0, higherConcern: false },",
    )

    js = js.replace(
        "Maestro integrado · Censo/Atlas + SUBTEL 4G/5G + Ookla Q1 2026",
        "Maestro integrado · Censo/Atlas + SUBTEL 4G/5G/RedAcceso + Mineduc + Ookla Q1 2026",
    )

    js = replace_once(
        js,
        "    Registros 5G: ${formatInt(d.mobile_5g_point_records_2025m03)} · operadores: ${formatValue(n(d.mobile_5g_operators_present_2025m03), indicators.mobile_5g_operators_present_2025m03)}<br>",
        "    Registros 5G: ${formatInt(d.mobile_5g_point_records_2025m03)} · operadores: ${formatValue(n(d.mobile_5g_operators_present_2025m03), indicators.mobile_5g_operators_present_2025m03)}<br>\n    Aulas Conectadas 2025: ${formatInt(d.mineduc_aulas_selected_establishments_2025)} seleccionados<br>\n    RedAcceso público: ${formatInt(d.fixed_access_public_operators_present)} operadores/entidades con trazado<br>",
    )

    js = replace_once(
        js,
        "    ['Operadores 5G', formatValue(n(d.mobile_5g_operators_present_2025m03), indicators.mobile_5g_operators_present_2025m03)],",
        "    ['Operadores 5G', formatValue(n(d.mobile_5g_operators_present_2025m03), indicators.mobile_5g_operators_present_2025m03)],\n    ['Aulas seleccionadas', formatInt(d.mineduc_aulas_selected_establishments_2025)],\n    ['Aulas seleccionadas rurales', formatInt(d.mineduc_aulas_selected_rural_establishments_2025)],\n    ['Aulas lista de espera', formatInt(d.mineduc_aulas_waitlist_establishments_2025)],\n    ['Matrícula en seleccionados', formatInt(d.mineduc_aulas_selected_enrollment_2025)],\n    ['Operadores RedAcceso público', formatInt(d.fixed_access_public_operators_present)],\n    ['Capas RedAcceso públicas', formatInt(d.fixed_access_public_layers_present)],\n    ['Trazado RedAcceso publicado', n(d.fixed_access_public_linework_length_km) === null ? 'N/D' : `${Number(d.fixed_access_public_linework_length_km).toLocaleString('es-CL', { maximumFractionDigits: 1 })} km`],",
    )

    # Do not show a placeholder for the expensive line-length layer. When that
    # field exists in the master, append it dynamically; otherwise omit it.
    unconditional = "    ['Capas RedAcceso públicas', formatInt(d.fixed_access_public_layers_present)],\n    ['Trazado RedAcceso publicado', n(d.fixed_access_public_linework_length_km) === null ? 'N/D' : `${Number(d.fixed_access_public_linework_length_km).toLocaleString('es-CL', { maximumFractionDigits: 1 })} km`],\n  ];\n  document.getElementById('detail-grid').innerHTML"
    conditional = "    ['Capas RedAcceso públicas', formatInt(d.fixed_access_public_layers_present)],\n  ];\n  if (n(d.fixed_access_public_linework_length_km) !== null) {\n    items.push(['Trazado RedAcceso publicado', `${Number(d.fixed_access_public_linework_length_km).toLocaleString('es-CL', { maximumFractionDigits: 1 })} km`]);\n  }\n  document.getElementById('detail-grid').innerHTML"
    if unconditional in js:
        js = js.replace(unconditional, conditional, 1)

    JS.write_text(js, encoding='utf-8')

    html = HTML.read_text(encoding='utf-8')
    new_footer = (
        'Fuentes principales: Censo de Población y Vivienda 2024, CASEN 2024, Encuestas de Acceso y Usos de Internet de SUBTEL, estadísticas sectoriales SUBTEL, Mineduc y Ookla Open Data. '
        'Los indicadores provienen de universos estadísticos distintos y no deben interpretarse como equivalentes. Ookla representa desempeño observado donde existieron tests. '
        'Los registros 4G/5G no son torres únicas. RedAcceso representa trazados regulatorios públicos y no disponibilidad comercial o cobertura de hogares. '
        'Aulas Conectadas representa selección administrativa de establecimientos y no conectividad domiciliaria de estudiantes. '
        'La dependencia móvil es una proxy operacional del proyecto, no una categoría oficial del Censo. '
        'El repositorio público no incluye el Índice de Vulnerabilidad Digital completo ni ponderadores propietarios.'
    )
    pattern = r'(<p class="footer-note">)\s*.*?\s*(</p>)'
    if not re.search(pattern, html, flags=re.DOTALL):
        raise RuntimeError('footer-note block not found')
    html = re.sub(pattern, rf'\1\n      {new_footer}\n    \2', html, count=1, flags=re.DOTALL)
    HTML.write_text(html, encoding='utf-8')

    print('Dashboard updated for education and fixed-access layers')


if __name__ == '__main__':
    main()
