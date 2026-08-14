from __future__ import annotations

from pathlib import Path
import pandas as pd

MASTER = Path('data/communal_master/chile_digital_inclusion_communes_2026_integrated.csv')
PRESENCE = Path('data/fixed_access_infrastructure/commune_fixed_access_presence.csv')
FIELDS = ['fixed_access_public_layers_present', 'fixed_access_public_operators_present']


def main():
    master = pd.read_csv(MASTER)
    fixed = pd.read_csv(PRESENCE)
    if len(master) != 346 or master['comuna'].nunique() != 346:
        raise RuntimeError('Master must have 346 unique communes')
    if len(fixed) != 346 or fixed['comuna'].nunique() != 346:
        raise RuntimeError('Fixed-access presence layer must have 346 unique communes')
    for field in FIELDS:
        if field in master.columns:
            master = master.drop(columns=[field])
    merged = master.merge(fixed[['comuna'] + FIELDS], on='comuna', how='left', validate='one_to_one')
    if merged[FIELDS].isna().any().any():
        raise RuntimeError('Fixed-access presence merge produced missing commune values')
    if int((merged['fixed_access_public_layers_present'] > 0).sum()) != 307:
        raise RuntimeError('Expected 307 communes with at least one public RedAcceso layer')
    merged.to_csv(MASTER, index=False)
    print('rows', len(merged), 'columns', len(merged.columns))
    print('communes_with_layer', int((merged['fixed_access_public_layers_present'] > 0).sum()))
    print('max_operators', int(merged['fixed_access_public_operators_present'].max()))

if __name__ == '__main__':
    main()
