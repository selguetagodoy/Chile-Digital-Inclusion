#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

SRC = Path('data/ookla/territorial/chile_2026q1_vs_2026q2_communes.csv')
OUT = Path('data/ookla/territorial/chile_2026q1_vs_2026q2_change_validation.csv')
SUMMARY = Path('data/ookla/territorial/chile_2026q1_vs_2026q2_test_reference.csv')


def main():
    df = pd.read_csv(SRC)
    required = {
        'commune_code','commune','province','region','network',
        'control_period','control_tests','control_download_mbps_test_weighted',
        'current_period','current_tests','current_download_mbps_test_weighted',
        'delta_download_mbps_test_weighted','delta_pct_download_mbps_test_weighted'
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f'Missing columns: {missing}')

    comparable = df.dropna(subset=['control_tests','current_tests','control_download_mbps_test_weighted','current_download_mbps_test_weighted']).copy()
    comparable['mean_tests_q1_q2'] = (comparable['control_tests'] + comparable['current_tests']) / 2.0

    refs = (
        comparable.groupby('network', as_index=False)
        .agg(
            comparable_communes=('commune_code','count'),
            mean_control_tests=('control_tests','mean'),
            mean_current_tests=('current_tests','mean'),
            mean_tests_q1_q2_reference=('mean_tests_q1_q2','mean'),
            total_control_tests=('control_tests','sum'),
            total_current_tests=('current_tests','sum'),
        )
    )

    comparable = comparable.merge(refs[['network','mean_tests_q1_q2_reference']], on='network', how='left')
    comparable['above_mean_tests_reference'] = comparable['mean_tests_q1_q2'] >= comparable['mean_tests_q1_q2_reference']
    comparable['validation_basis'] = 'descriptive_mean_test_count_not_statistical_representativeness'

    # Rank change only among rows that meet the descriptive mean-test reference.
    validated = comparable['above_mean_tests_reference']
    comparable['rank_change_desc_validated'] = pd.NA
    comparable['rank_change_asc_validated'] = pd.NA
    for network in sorted(comparable['network'].dropna().unique()):
        mask = validated & (comparable['network'] == network)
        comparable.loc[mask, 'rank_change_desc_validated'] = comparable.loc[mask, 'delta_pct_download_mbps_test_weighted'].rank(method='min', ascending=False).astype('Int64')
        comparable.loc[mask, 'rank_change_asc_validated'] = comparable.loc[mask, 'delta_pct_download_mbps_test_weighted'].rank(method='min', ascending=True).astype('Int64')

    cols = [
        'commune_code','commune','province','region','network',
        'control_period','control_tests','control_download_mbps_test_weighted',
        'current_period','current_tests','current_download_mbps_test_weighted',
        'mean_tests_q1_q2','mean_tests_q1_q2_reference','above_mean_tests_reference',
        'delta_download_mbps_test_weighted','delta_pct_download_mbps_test_weighted',
        'rank_change_desc_validated','rank_change_asc_validated','validation_basis'
    ]
    comparable[cols].sort_values(['network','delta_pct_download_mbps_test_weighted'], ascending=[True,False]).to_csv(OUT, index=False)

    counts = (
        comparable.groupby('network', as_index=False)
        .agg(
            comparable_rows=('commune_code','count'),
            rows_at_or_above_mean=('above_mean_tests_reference','sum')
        )
    )
    refs = refs.merge(counts, on='network', how='left')
    refs['share_rows_at_or_above_mean_pct'] = refs['rows_at_or_above_mean'] / refs['comparable_rows'] * 100.0
    refs['reference_rule'] = 'mean of commune-level average tests across Q1 and Q2; descriptive QA only'
    refs.to_csv(SUMMARY, index=False)

    print(f'wrote {len(comparable)} comparable commune-network rows -> {OUT}')
    print(refs.to_string(index=False))


if __name__ == '__main__':
    main()
