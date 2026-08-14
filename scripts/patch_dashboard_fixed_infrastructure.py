#!/usr/bin/env python3
from pathlib import Path
p=Path('assets/dashboard.js')
s=p.read_text(encoding='utf-8')
needle="  mobile_5g_operators_present_2025m03: { label: 'Operadores con registros 5G · Mar 2025', unit: '', digits: 0, higherConcern: false },\n"
insert=needle+"  subtel_fixed_residential_per_100_censo_households_2026m03: { label: 'Conexiones fijas residenciales por 100 hogares · Mar 2026', unit: '', digits: 1, higherConcern: false },\n"
if 'subtel_fixed_residential_per_100_censo_households_2026m03' not in s:
    if needle not in s: raise SystemExit('indicator insertion point not found')
    s=s.replace(needle,insert,1)
needle2="    ['Operadores 5G', formatValue(n(d.mobile_5g_operators_present_2025m03), indicators.mobile_5g_operators_present_2025m03)],\n"
insert2=needle2+"    ['Fijo residencial / 100 hogares', formatValue(n(d.subtel_fixed_residential_per_100_censo_households_2026m03), indicators.subtel_fixed_residential_per_100_censo_households_2026m03)],\n    ['Conexiones fijas residenciales', formatInt(d.subtel_fixed_connections_residential_2026m03)],\n"
if "['Fijo residencial / 100 hogares'" not in s:
    if needle2 not in s: raise SystemExit('detail insertion point not found')
    s=s.replace(needle2,insert2,1)
p.write_text(s,encoding='utf-8')
print('dashboard fixed-infrastructure fields patched')
