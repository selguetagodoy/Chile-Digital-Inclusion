#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

BASE = Path('data/ookla/territorial')
CHANGE_IN = BASE / 'chile_2026q1_vs_2026q2_change_validation.csv'
REGION_IN = BASE / 'chile_2026q1_vs_2026q2_regions.csv'
CHANGE_OUT = BASE / 'chile_2026q1_vs_2026q2_changes_report_validated.csv'
REGION_OUT = BASE / 'chile_2026q2_regions_report.csv'


def boolish(s):
    return s.astype(str).str.strip().str.lower().eq('true')


def main():
    ch = pd.read_csv(CHANGE_IN)
    fixed = ch[(ch.network == 'fixed') & boolish(ch['above_mean_tests_reference'])].copy()
    mobile = ch[(ch.network == 'mobile') & (ch['mean_tests_q1_q2'] >= 1000)].copy()
    fixed['report_validation'] = 'fixed_mean_tests_q1_q2_at_or_above_national_communal_mean'
    mobile['report_validation'] = 'mobile_mean_tests_q1_q2_at_or_above_1000'
    out = pd.concat([fixed, mobile], ignore_index=True)
    delta_pct = 'delta_pct_download_mbps_test_weighted'
    delta_abs = 'delta_download_mbps_test_weighted'
    out = out.sort_values(['network', delta_pct], ascending=[True,False], kind='mergesort')
    out['report_change_rank_desc'] = out.groupby('network')[delta_pct].rank(method='min', ascending=False).astype(int)
    out['report_change_rank_asc'] = out.groupby('network')[delta_pct].rank(method='min', ascending=True).astype(int)
    keep = ['commune_code','commune','province','region','network','control_period','control_tests',
            'control_download_mbps_test_weighted','current_period','current_tests',
            'current_download_mbps_test_weighted','mean_tests_q1_q2',delta_abs,
            delta_pct,'report_change_rank_desc','report_change_rank_asc','report_validation']
    out[keep].to_csv(CHANGE_OUT, index=False)

    rg = pd.read_csv(REGION_IN)
    rg = rg.sort_values(['network','current_download_mbps_test_weighted'], ascending=[True,False], kind='mergesort')
    rg['q2_speed_rank'] = rg.groupby('network')['current_download_mbps_test_weighted'].rank(method='min', ascending=False).astype(int)
    rg['q1_q2_change_rank'] = rg.groupby('network')['delta_pct_download_mbps_test_weighted'].rank(method='min', ascending=False).astype(int)
    rkeep = ['region_code','region','network','control_period','control_tests','control_download_mbps_test_weighted',
             'current_period','current_tests','current_download_mbps_test_weighted','delta_pct_download_mbps_test_weighted',
             'current_latency_ms_test_weighted','q2_speed_rank','q1_q2_change_rank']
    rg[rkeep].to_csv(REGION_OUT, index=False)

    print(f'changes: fixed={len(fixed)} mobile={len(mobile)}')
    for network in ['fixed','mobile']:
        s = out[out.network == network].sort_values(delta_pct, ascending=False)
        print(network, 'improvements')
        print(s.head(10)[['commune',delta_pct,'mean_tests_q1_q2']].to_string(index=False))
        print(network, 'declines')
        print(s.tail(10).sort_values(delta_pct)[['commune',delta_pct,'mean_tests_q1_q2']].to_string(index=False))


if __name__ == '__main__':
    main()
