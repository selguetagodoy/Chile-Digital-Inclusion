from __future__ import annotations

import csv
from pathlib import Path
import requests

OUT = Path('data/fixed_access_infrastructure/attribute_profile.csv')

LAYERS = [
    ('Claro', 'https://licancabur.subtel.gob.cl/server/rest/services/Of468_Claro_RedAcceso/FeatureServer/0', ['nomb_red','tipo_tendi']),
    ('Entel', 'https://licancabur.subtel.gob.cl/server/rest/services/Of468_Entel_RedAcceso_primarias/FeatureServer/0', ['tipo_red','fijacion']),
]


def query(url: str, params: dict):
    r = requests.get(url + '/query', params=params, timeout=90)
    r.raise_for_status()
    data = r.json()
    if data.get('error'):
        raise RuntimeError(data['error'])
    return data


def distinct_counts(url: str, field: str):
    stats = [{
        'statisticType': 'count',
        'onStatisticField': 'OBJECTID',
        'outStatisticFieldName': 'n_records',
    }]
    data = query(url, {
        'where':'1=1', 'f':'json', 'returnGeometry':'false',
        'outStatistics': __import__('json').dumps(stats),
        'groupByFieldsForStatistics': field,
        'orderByFields':'n_records DESC',
        'outFields': field,
    })
    return [f.get('attributes', {}) for f in data.get('features', [])]


def numeric_summary(url: str, field: str):
    import json
    stats = []
    for stat in ['count','min','max','avg','sum']:
        stats.append({'statisticType':stat,'onStatisticField':field,'outStatisticFieldName':stat})
    data = query(url, {'where':f'{field} IS NOT NULL','f':'json','returnGeometry':'false','outStatistics':json.dumps(stats)})
    feats = data.get('features', [])
    return feats[0].get('attributes', {}) if feats else {}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    for operator, url, fields in LAYERS:
        for field in fields:
            for attrs in distinct_counts(url, field):
                rows.append({
                    'operator':operator,'profile_type':'category','field':field,
                    'value':attrs.get(field,''),'n_records':attrs.get('n_records',''),
                    'count':'','min':'','max':'','avg':'','sum':'','source_url':url,
                })

    numeric = [
        ('Claro','https://licancabur.subtel.gob.cl/server/rest/services/Of468_Claro_RedAcceso/FeatureServer/0','capacidad'),
        ('Entel','https://licancabur.subtel.gob.cl/server/rest/services/Of468_Entel_RedAcceso_primarias/FeatureServer/0','fiber_coun'),
    ]
    for operator,url,field in numeric:
        s=numeric_summary(url,field)
        rows.append({
            'operator':operator,'profile_type':'numeric_summary','field':field,'value':'','n_records':'',
            'count':s.get('count',''),'min':s.get('min',''),'max':s.get('max',''),'avg':s.get('avg',''),'sum':s.get('sum',''),'source_url':url,
        })

    fields=['operator','profile_type','field','value','n_records','count','min','max','avg','sum','source_url']
    with OUT.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f'wrote {len(rows)} rows')

if __name__=='__main__':
    main()
