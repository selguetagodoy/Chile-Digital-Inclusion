from pathlib import Path

import pandas as pd

INPUT = Path('data/ookla/territorial/chile_2026q1_vs_2026q2_change_validation.csv')
OUTPUT = Path('data/ookla/territorial/chile_2026q2_speed_rankings_validated.csv')


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.strip().str.lower().eq('true')


def main() -> None:
    df = pd.read_csv(INPUT)
    df = df[as_bool(df['above_mean_tests_reference'])].copy()

    keep = [
        'commune_code', 'commune', 'province', 'region', 'network',
        'current_period', 'current_tests', 'current_download_mbps_test_weighted',
        'mean_tests_q1_q2', 'mean_tests_q1_q2_reference',
        'above_mean_tests_reference'
    ]
    df = df[keep]

    outputs = []
    for network in ['fixed', 'mobile']:
        sub = df[df['network'].eq(network)].copy()
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
        sub['validation_basis'] = 'above_mean_q1_q2_test_volume_descriptive_not_statistical_representativeness'
        outputs.append(sub)

    out = pd.concat(outputs, ignore_index=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False)

    for network in ['fixed', 'mobile']:
        sub = out[out['network'].eq(network)]
        print(f'{network}: validated_communes={len(sub)}')
        print('top5')
        print(sub.head(5)[['commune','current_download_mbps_test_weighted','current_tests','mean_tests_q1_q2']].to_string(index=False))
        print('bottom5')
        print(sub.tail(5)[['commune','current_download_mbps_test_weighted','current_tests','mean_tests_q1_q2']].to_string(index=False))


if __name__ == '__main__':
    main()
