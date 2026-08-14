from __future__ import annotations

from pathlib import Path
import pandas as pd

MASTER = Path('data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv')
EDUCATION = Path('data/education_connectivity_2026/aulas_conectadas_2025_commune_summary.csv')

FIELDS = [
    'mineduc_aulas_selected_establishments_2025',
    'mineduc_aulas_waitlist_establishments_2025',
    'mineduc_aulas_selected_rural_establishments_2025',
    'mineduc_aulas_selected_enrollment_2025',
    'mineduc_aulas_selected_with_coordinates_2025',
]


def main() -> None:
    master = pd.read_csv(MASTER)
    edu = pd.read_csv(EDUCATION)

    if len(master) != 346 or master['comuna'].nunique() != 346:
        raise RuntimeError('Integrated master must contain exactly 346 unique communes')
    if len(edu) != 346 or edu['comuna'].nunique() != 346:
        raise RuntimeError('Education communal summary must contain exactly 346 unique communes')

    for field in FIELDS:
        if field not in edu.columns:
            raise RuntimeError(f'Missing education field: {field}')
        if field in master.columns:
            master = master.drop(columns=[field])

    merged = master.merge(edu[['comuna'] + FIELDS], on='comuna', how='left', validate='one_to_one')
    if merged[FIELDS].isna().any().any():
        missing = merged.loc[merged[FIELDS].isna().any(axis=1), ['comuna', 'comuna_nombre']]
        raise RuntimeError(f'Education merge left missing commune rows: {missing.to_dict("records")[:10]}')

    numeric = merged[FIELDS].apply(pd.to_numeric, errors='raise')
    if int(numeric['mineduc_aulas_selected_establishments_2025'].sum()) != 700:
        raise RuntimeError('Selected Aulas Conectadas count does not sum to 700')
    if int(numeric['mineduc_aulas_waitlist_establishments_2025'].sum()) != 93:
        raise RuntimeError('Aulas Conectadas waitlist does not sum to 93')

    merged.to_csv(MASTER, index=False)
    print('rows', len(merged), 'columns', len(merged.columns))
    print('selected', int(numeric['mineduc_aulas_selected_establishments_2025'].sum()))
    print('waitlist', int(numeric['mineduc_aulas_waitlist_establishments_2025'].sum()))
    print('communes_selected', int((numeric['mineduc_aulas_selected_establishments_2025'] > 0).sum()))


if __name__ == '__main__':
    main()
