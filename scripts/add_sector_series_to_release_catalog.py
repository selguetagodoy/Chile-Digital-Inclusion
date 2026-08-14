from pathlib import Path

PATH = Path('scripts/build_release_metadata.py')

BLOCK = """    {
        'layer_id': 'subtel_sector_longitudinal_2026m03',
        'path': 'data/subtel_sector_series/sector_core_monthly_long.csv',
        'source_family': 'SUBTEL administrative Internet series',
        'reference_period': 'effective workbook ranges through 2026-03',
        'territorial_level': 'national monthly',
        'statistical_unit': 'connection / traffic aggregate',
        'role': 'canonical longitudinal fixed/mobile connection and traffic series',
        'canonical': 'yes',
        'license_note': 'Public official XLSX sources; provenance discrepancies are retained rather than force-reconciled',
    },
"""

MARKER = "    {\n        'layer_id': 'subtel_oti_fixed_speed_2026m01',"


def main():
    text = PATH.read_text(encoding='utf-8')
    if "'layer_id': 'subtel_sector_longitudinal_2026m03'" in text:
        print('Layer already registered')
        return
    if MARKER not in text:
        raise RuntimeError('Could not locate OTI layer marker in build_release_metadata.py')
    text = text.replace(MARKER, BLOCK + MARKER, 1)
    PATH.write_text(text, encoding='utf-8')
    print('Registered longitudinal SUBTEL sector series in release catalog builder')

if __name__ == '__main__':
    main()
