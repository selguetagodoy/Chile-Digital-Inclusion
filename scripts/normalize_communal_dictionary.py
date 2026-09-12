#!/usr/bin/env python3
"""Normalize period-aware labels in the generated communal master dictionary.

The base dictionary builder intentionally provides generic metadata for new
integrated fields. This post-build normalizer corrects descriptions whose
variable name carries an explicit comparison period, without modifying older
historical comparison fields.
"""

from __future__ import annotations

import csv
from pathlib import Path

CSV_PATH = Path('data/metadata/communal_master_dictionary.csv')
MD_PATH = Path('docs/communal_master_dictionary.md')

OLD = 'Q4 2025 a Q1 2026'
NEW = 'Q1 2026 a Q2 2026'
TOKEN = '_q1_to_q2'


def normalize_csv() -> int:
    with CSV_PATH.open(encoding='utf-8', newline='') as fh:
        reader = csv.DictReader(fh)
        fields = reader.fieldnames or []
        rows = list(reader)

    changed = 0
    for row in rows:
        if TOKEN in row.get('variable', ''):
            for field in ('label_es', 'description', 'comparison_note'):
                value = row.get(field, '')
                corrected = value.replace(OLD, NEW)
                if corrected != value:
                    row[field] = corrected
                    changed += 1

    with CSV_PATH.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return changed


def normalize_markdown() -> int:
    text = MD_PATH.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)
    changed = 0
    out = []
    for line in lines:
        if TOKEN in line and OLD in line:
            line = line.replace(OLD, NEW)
            changed += 1
        out.append(line)
    MD_PATH.write_text(''.join(out), encoding='utf-8')
    return changed


def main() -> None:
    csv_changes = normalize_csv()
    md_changes = normalize_markdown()
    print(f'normalized_dictionary_csv_fields={csv_changes}')
    print(f'normalized_dictionary_markdown_lines={md_changes}')


if __name__ == '__main__':
    main()
