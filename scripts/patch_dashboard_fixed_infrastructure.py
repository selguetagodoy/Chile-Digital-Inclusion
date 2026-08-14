#!/usr/bin/env python3
from pathlib import Path
p=Path('assets/dashboard.js')
s=p.read_text(encoding='utf-8')
field='subtel_fixed_residential_per_100_censo_households_2026m03'
needle="  fixed_access_public_operators_present: { label: 'Operadores con trazado RedAcceso público', unit: '', digits: 0, higherConcern: false },\n"
insert=needle+"  subtel_fixed_residential_per_100_censo_households_2026m03: { label: 'Conexiones fijas residenciales por 100 hogares · mar 2026', unit: '', digits: 1, higherConcern: false },\n"
if field not in s:
    if needle not in s: raise SystemExit('indicator insertion point not found')
    s=s.replace(needle,insert,1)
needle2="    ['Operadores RedAcceso público', formatInt(d.fixed_access_public_operators_present)],\n"
insert2="    ['Fijo residencial / 100 hogares', formatValue(n(d.subtel_fixed_residential_per_100_censo_households_2026m03), indicators.subtel_fixed_residential_per_100_censo_households_2026m03)],\n    ['Conexiones fijas residenciales', formatInt(d.subtel_fixed_connections_residential_2026m03)],\n"+needle2
if "['Fijo residencial / 100 hogares'" not in s:
    if needle2 not in s: raise SystemExit('detail insertion point not found')
    s=s.replace(needle2,insert2,1)
p.write_text(s,encoding='utf-8')
print('dashboard fixed-infrastructure fields patched')
