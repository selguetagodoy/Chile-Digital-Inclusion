from __future__ import annotations

import csv
from pathlib import Path
import requests

ROOT='https://licancabur.subtel.gob.cl/server/rest/services'
OUT=Path('data/fixed_access_infrastructure/service_discovery.csv')


def get(url,params=None):
    r=requests.get(url,params=params or {'f':'json'},timeout=90); r.raise_for_status()
    data=r.json()
    if isinstance(data,dict) and data.get('error'):
        raise RuntimeError(data['error'])
    return data


def scan(url: str, folder: str=''):
    data=get(url,{'f':'json'})
    rows=[]
    for s in data.get('services',[]):
        name=s.get('name',''); typ=s.get('type','')
        if 'redacceso' in name.lower():
            rows.append({'folder':folder,'service_name':name,'service_type':typ,'service_url':f'{ROOT}/{name}/{typ}'})
    for sub in data.get('folders',[]):
        if sub in {'System','Utilities','Hosted'}:
            continue
        suburl=f'{ROOT}/{sub}'
        try:
            rows.extend(scan(suburl,sub if not folder else f'{folder}/{sub}'))
        except Exception as exc:
            rows.append({'folder':sub,'service_name':'','service_type':'','service_url':f'ERROR: {type(exc).__name__}: {exc}'})
    return rows


def main():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    rows=scan(ROOT)
    fields=['folder','service_name','service_type','service_url']
    with OUT.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print('RedAcceso matches',sum(bool(r['service_name']) for r in rows),'errors',sum(not r['service_name'] for r in rows))
    for r in rows:
        print(r)

if __name__=='__main__':
    main()
