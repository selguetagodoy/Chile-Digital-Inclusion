#!/usr/bin/env python3
from pathlib import Path
p=Path('scripts/validate_public_release.py')
s=p.read_text(encoding='utf-8')
# Add fixed subscription paths
needle="FIXED_QA = ROOT / 'data/fixed_access_infrastructure/presence_query_qa.csv'\n"
add=needle+"FIXED_SUB = ROOT / 'data/fixed_infrastructure_2026/commune_fixed_connections_2026_03.csv'\nFIXED_SUB_QA = ROOT / 'data/fixed_infrastructure_2026/source_match_qa.csv'\nFIXED_SUB_MISSING = ROOT / 'data/fixed_infrastructure_2026/source_not_reported_communes.csv'\n"
if 'FIXED_SUB =' not in s:
    if needle not in s: raise SystemExit('fixed path marker missing')
    s=s.replace(needle,add,1)
# Add required fields
needle2="    'fixed_access_public_operators_present',\n"
add2=needle2+"    'subtel_fixed_connections_total_2026m03',\n    'subtel_fixed_connections_residential_2026m03',\n    'subtel_fixed_residential_share_pct_2026m03',\n    'subtel_fixed_residential_per_100_censo_households_2026m03',\n    'subtel_fixed_source_status_2026m03',\n"
if "'subtel_fixed_connections_total_2026m03'" not in s[s.find('REQUIRED_MASTER'):s.find('REQUIRED_SECTOR')]:
    if needle2 not in s: raise SystemExit('required field marker missing')
    s=s.replace(needle2,add2,1)
# Required files
old="MOBILE, MOBILE_QA, FIXED, FIXED_QA, SECTOR"
new="MOBILE, MOBILE_QA, FIXED, FIXED_QA, FIXED_SUB, FIXED_SUB_QA, FIXED_SUB_MISSING, SECTOR"
if old in s:s=s.replace(old,new,1)
# Column count
s=s.replace("len(master_fields) == 84, f'{len(master_fields)} variables'","len(master_fields) == 89, f'{len(master_fields)} variables'",1)
# Insert fixed subscription QA before GEO block
marker="    with GEO.open(encoding='utf-8') as fh:\n"
block="""    fixed_sub = read_csv(FIXED_SUB)
    fixed_sub_reported = sum(r['source_status'] == 'reported' for r in fixed_sub)
    fixed_sub_unmatched = read_csv(FIXED_SUB_QA)
    fixed_sub_missing = read_csv(FIXED_SUB_MISSING)
    results.append(check('fixed_subscription_rows', len(fixed_sub) == 346, f'{len(fixed_sub)} commune rows'))
    results.append(check('fixed_subscription_reported', fixed_sub_reported == 342, f'{fixed_sub_reported} communes reported by source'))
    results.append(check('fixed_subscription_unmatched_source', len(fixed_sub_unmatched) == 0, f'{len(fixed_sub_unmatched)} unresolved source rows'))
    results.append(check('fixed_subscription_source_not_reported', len(fixed_sub_missing) == 4, f'{len(fixed_sub_missing)} catalogue communes not reported by source'))

"""
if "fixed_subscription_rows" not in s:
    if marker not in s: raise SystemExit('GEO insertion marker missing')
    s=s.replace(marker,block+marker,1)
# Dashboard ref
needle3="        'fixed_access_public_operators_present',\n"
if "'subtel_fixed_residential_per_100_censo_households_2026m03'," not in s[s.find("for ref in ["):]:
    pos=s.find("for ref in [")
    idx=s.find(needle3,pos)
    if idx<0:raise SystemExit('dashboard reference marker missing')
    s=s[:idx]+s[idx:].replace(needle3,needle3+"        'subtel_fixed_residential_per_100_censo_households_2026m03',\n",1)
p.write_text(s,encoding='utf-8')
print('public-release QA patched for fixed subscriptions')
