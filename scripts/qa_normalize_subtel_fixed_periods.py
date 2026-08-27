from __future__ import annotations

import csv
from pathlib import Path

OUTDIR = Path('data/subtel_sector_series')


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def dedupe_keep_latest_source_row(rows: list[dict], key_fields: tuple[str, ...]) -> list[dict]:
    chosen: dict[tuple[str, ...], dict] = {}
    for row in rows:
        key = tuple(row[f] for f in key_fields)
        prior = chosen.get(key)
        if prior is None:
            chosen[key] = row
            continue
        current_source_row = int(float(row.get('source_row') or 0))
        prior_source_row = int(float(prior.get('source_row') or 0))
        if current_source_row >= prior_source_row:
            chosen[key] = row
    return list(chosen.values())


def period_sort_key(row: dict):
    return (row.get('period', ''), row.get('series_group', ''), row.get('indicator', ''))


def main() -> None:
    fixed_path = OUTDIR / 'fixed_connections_monthly.csv'
    fixed_rows = read_csv(fixed_path)
    fixed_fields = list(fixed_rows[0].keys())
    fixed_clean = dedupe_keep_latest_source_row(fixed_rows, ('period',))
    fixed_clean.sort(key=lambda r: r['period'])
    write_csv(fixed_path, fixed_clean, fixed_fields)

    core_path = OUTDIR / 'sector_core_monthly_long.csv'
    core_rows = read_csv(core_path)
    core_fields = list(core_rows[0].keys())
    core_clean = dedupe_keep_latest_source_row(core_rows, ('period', 'series_group', 'indicator'))
    core_clean.sort(key=period_sort_key)
    write_csv(core_path, core_clean, core_fields)

    annual_path = OUTDIR / 'sector_core_december_long_2000_2025.csv'
    annual_rows = read_csv(annual_path)
    annual_fields = list(annual_rows[0].keys())
    annual_clean = dedupe_keep_latest_source_row(annual_rows, ('period', 'series_group', 'indicator'))
    annual_clean.sort(key=period_sort_key)
    write_csv(annual_path, annual_clean, annual_fields)

    qa_path = OUTDIR / 'series_qa.csv'
    qa_rows = read_csv(qa_path)
    qa_fields = list(qa_rows[0].keys())
    for row in qa_rows:
        if row['check'] == 'fixed_connections_rows':
            row['value'] = str(len(fixed_clean))
            row['expectation'] = str(len(fixed_clean))
        elif row['check'] == 'fixed_connections_unique_periods':
            row['value'] = str(len({r['period'] for r in fixed_clean}))
            row['expectation'] = str(len(fixed_clean))
    write_csv(qa_path, qa_rows, qa_fields)

    if len(fixed_clean) != len({r['period'] for r in fixed_clean}):
        raise RuntimeError('Duplicate periods remain in fixed_connections_monthly.csv')
    if fixed_clean[-1]['period'] != '2026-06':
        raise RuntimeError('Fixed series no longer ends in 2026-06')

    print('fixed rows before', len(fixed_rows), 'after', len(fixed_clean))
    print('fixed first/last', fixed_clean[0]['period'], fixed_clean[-1]['period'])
    print('core rows before', len(core_rows), 'after', len(core_clean))
    print('annual rows before', len(annual_rows), 'after', len(annual_clean))


if __name__ == '__main__':
    main()
