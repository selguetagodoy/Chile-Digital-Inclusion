#!/usr/bin/env python3
"""Guard the fixed-subscription public QA contract without rewriting it backwards.

The public validator now contains the complete reconciled March-2026 contract.
This helper is retained because an existing workflow invokes it, but it only
verifies that the current validator has the expected modern checks; it no longer
injects the superseded 342/346 and four-missing-communes assumptions.
"""
from pathlib import Path

p = Path('scripts/validate_public_release.py')
s = p.read_text(encoding='utf-8')

required_fragments = [
    "FIXED_SUB_ALIGNMENT = ROOT / 'data/fixed_infrastructure_2026/source_alignment_qa.csv'",
    'EXPECTED_FIXED_SOURCE_BLANK = {12202}',
    "fixed_sub_reported == 345",
    "len(fixed_sub_missing) == 1",
    "source_blank_statuses == {'source_blank'}",
    "len(fixed_sub_alignment) == 32",
    "'subtel_fixed_residential_per_100_censo_households_2026m03'",
]
missing = [fragment for fragment in required_fragments if fragment not in s]
if missing:
    raise SystemExit(f'Current fixed-subscription QA contract is incomplete: {missing}')

print('public-release QA already uses reconciled fixed-subscription contract')
