#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

src = Path('data/subtel_microdata/harmonization_candidates.csv')
out = Path('data/subtel_microdata/top_harmonization_candidates.csv')

df = pd.read_csv(src, dtype=str).fillna('')
df['score_num'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
df['nonmissing_num'] = pd.to_numeric(df['nonmissing_n'], errors='coerce').fillna(0)
df['distinct_num'] = pd.to_numeric(df['distinct_values'], errors='coerce').fillna(0)

# Prefer strong lexical matches, broad non-missing coverage and reasonably compact variables.
df['compact_bonus'] = ((df['distinct_num'] >= 2) & (df['distinct_num'] <= 40)).astype(int)
df = df.sort_values(
    ['reference_year', 'survey_wave', 'domain', 'score_num', 'compact_bonus', 'nonmissing_num'],
    ascending=[False, True, True, False, False, False],
)

top = df.groupby(['reference_year', 'survey_wave', 'domain'], as_index=False, group_keys=False).head(8)
cols = [
    'reference_year','survey_wave','domain','score','variable','label',
    'nonmissing_n','distinct_values','missing_pct','has_value_labels'
]
top[cols].to_csv(out, index=False, encoding='utf-8')
print(f'Wrote {len(top)} crosswalk candidate rows to {out}')
