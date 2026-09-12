from pathlib import Path

import pandas as pd

INPUT = Path('data/ookla/territorial/chile_2026q1_vs_2026q2_change_validation.csv')
OUTPUT = Path('data/ookla/territorial/chile_2026q2_speed_rankings_validated.csv')
MOBILE_MIN_MEAN_TESTS = 1000.0


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.lower().eq('true')


def main() -> None:
    source = pd.read_csv(INPUT)

    fixed = source[
        source['network'].eq('fixed') & as_bool(source['above_mean_tests_reference'])
    ].copy()
    fixed['validation_basis'] = (
        'fixed_above_mean_q1_q2_test_volume_descriptive_not_statistical_representativeness'
    )

    mobile = source[
        source['network'].eq('mobile')
        & source['mean_tests_q1_q2'].ge(MOBILE_MIN_MEAN_TESTS)
    ].copy()
    mobile['validation_basis'] = (
        'mobile_mean_q1_q2_tests_ge_1000_descriptive_not_statistical_representativeness'
    )

    keep = [
        'commune_code', 'commune', 'province', 'region', 'network',
        'current_period', 'current_tests', 'current_download_mbps_test_weighted',
        'mean_tests_q1_q2', 'mean_tests_q1_q2_reference',
        'above_mean_tests_reference', 'validation_basis'
    ]

    outputs = []
    for sub in [fixed, mobile]:
        sub = sub[keep].copy()
        sub = sub.sort_values(
            ['current_download_mbps_test_weighted', 'mean_tests_q1_q2', 'commune'],
            ascending=[False, False, True],
            kind='mergesort'
        ).reset_index(drop=True)
        sub['rank_speed_desc_validated'] = range(1, len(sub) + 1)
        sub['rank_speed_asc_validated'] = (
            sub['current_download_mbps_test_weighted']
            .rank(method='min', ascending=True)
            .astype(int)
        )
        outputs.append(sub)

    out = pd.concat(outputs, ignore_index=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False)

    for network in ['fixed', 'mobile']:
        sub = out[out['network'].eq(network)]
        print(f'{network}: validated_communes={len(sub)}')
        print('top10')
        print(sub.head(10)[['commune','current_download_mbps_test_weighted','current_tests','mean_tests_q1_q2']].to_string(index=False))
        print('bottom10')
        print(sub.tail(10)[['commune','current_download_mbps_test_weighted','current_tests','mean_tests_q1_q2']].to_string(index=False))


if __name__ == '__main__':
    main()
