#!/usr/bin/env python3
"""Build reproducible commune rankings from Ookla Chile Q2 2026 territorial data.

No observations are excluded by an arbitrary sample threshold. The output retains
`tests` and `tiles` so users can assess the observational support behind each rank.
"""
from pathlib import Path
import pandas as pd

SRC = Path('data/ookla/territorial/chile_2026q2_communes.csv')
OUT = Path('data/ookla/territorial/chile_2026q2_commune_rankings.csv')


def main() -> None:
    df = pd.read_csv(SRC)
    required = {
        'commune_code','commune','province','region','period','network','tiles','tests',
        'download_mbps_test_weighted','upload_mbps_test_weighted','latency_ms_test_weighted'
    }
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f'Missing required columns: {sorted(missing)}')
    if set(df['period'].dropna().astype(str)) != {'2026Q2'}:
        raise SystemExit('Expected only period 2026Q2')

    frames = []
    for network, part in df.groupby('network', dropna=False):
        part = part.copy()
        n = len(part)
        part['observed_communes_network'] = n
        part['rank_download_desc'] = part['download_mbps_test_weighted'].rank(method='min', ascending=False, na_option='bottom').astype('Int64')
        part['rank_upload_desc'] = part['upload_mbps_test_weighted'].rank(method='min', ascending=False, na_option='bottom').astype('Int64')
        part['rank_latency_asc'] = part['latency_ms_test_weighted'].rank(method='min', ascending=True, na_option='bottom').astype('Int64')
        frames.append(part)

    out = pd.concat(frames, ignore_index=True)
    cols = [
        'commune_code','commune','province','region','period','network','tiles','tests',
        'download_mbps_test_weighted','rank_download_desc',
        'upload_mbps_test_weighted','rank_upload_desc',
        'latency_ms_test_weighted','rank_latency_asc','observed_communes_network'
    ]
    out = out[cols].sort_values(['network','rank_download_desc','commune_code'], kind='stable')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)

    for network, part in out.groupby('network'):
        print(f'{network}: rows={len(part)}, tests={int(part.tests.fillna(0).sum())}')
        print('top5 download')
        print(part[['rank_download_desc','commune','region','download_mbps_test_weighted','tests']].head(5).to_string(index=False))
        print('bottom5 download')
        print(part[['rank_download_desc','commune','region','download_mbps_test_weighted','tests']].tail(5).to_string(index=False))


if __name__ == '__main__':
    main()
