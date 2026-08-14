#!/usr/bin/env python3
"""Recover the 2011 person-level SAV using legacy encodings and publish aggregates."""
from __future__ import annotations
import json, tempfile, zipfile
from pathlib import Path
import pandas as pd
import pyreadstat, requests

URL='https://www.subtel.gob.cl/images/stories/apoyo_articulos/estudios/base_datos_final_2.zip'
OUT=Path('data/subtel_2011_person')

def read_robust(path):
    errs=[]
    for enc in ['latin1','windows-1252','utf-8']:
        try:
            return pyreadstat.read_sav(str(path), encoding=enc, apply_value_formats=False, formats_as_category=False, user_missing=False), enc
        except Exception as e: errs.append(f'{enc}: {e!r}')
    raise RuntimeError(' | '.join(errs))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); z=td/'src.zip'
        r=requests.get(URL,headers={'User-Agent':'Chile-Digital-Inclusion/1.0'},timeout=120); r.raise_for_status(); z.write_bytes(r.content)
        ex=td/'ex'; ex.mkdir(); zipfile.ZipFile(z).extractall(ex)
        candidates=[p for p in ex.rglob('*.sav') if 'persona' in p.name.lower() and not p.name.startswith('._')]
        if not candidates: raise RuntimeError('2011 person SAV not found')
        (df,meta),enc=read_robust(candidates[0])
        labels=meta.column_names_to_labels or {}; vlabels=meta.variable_value_labels or {}
        vars=[]; cats=[]; nums=[]
        for col in df.columns:
            s=df[col]; non=s.dropna(); d=int(non.nunique()); label=labels.get(col,'') or ''
            vars.append({'variable':col,'label':label,'dtype':str(s.dtype),'nonmissing_n':int(s.notna().sum()),'distinct_values':d,'missing_pct':round(float(s.isna().mean()*100),4),'value_labels_json':json.dumps(vlabels.get(col,{}) or {},ensure_ascii=False)})
            if 2<=d<=40 and len(non)>=100:
                vc=non.value_counts(sort=False); den=int(vc.sum())
                for val,n in vc.items():
                    n=int(n)
                    if n<30: continue
                    lbl=(vlabels.get(col,{}) or {}).get(val,str(val))
                    cats.append({'variable':col,'variable_label':label,'category_code':val,'category_label':lbl,'n_unweighted':n,'pct_unweighted':round(n/den*100,5),'cell_rule':'n >= 30'})
            elif pd.api.types.is_numeric_dtype(s) and d>40 and len(non)>=100:
                x=pd.to_numeric(s,errors='coerce').dropna(); nums.append({'variable':col,'variable_label':label,'n_unweighted':int(x.size),'mean':round(float(x.mean()),6),'median':round(float(x.median()),6),'min':round(float(x.min()),6),'max':round(float(x.max()),6)})
    pd.DataFrame(vars).to_csv(OUT/'variable_dictionary.csv',index=False)
    pd.DataFrame(cats).to_csv(OUT/'categorical_distributions.csv',index=False)
    pd.DataFrame(nums).to_csv(OUT/'numeric_summary.csv',index=False)
    pd.DataFrame([{'reference_year':2011,'survey_wave':'III','dataset':'person','rows':len(df),'columns':len(df.columns),'encoding':enc,'source_url':URL}]).to_csv(OUT/'dataset_manifest.csv',index=False)
    summary={'datasets_processed':1,'variables_profiled':len(vars),'categorical_rows':len(cats),'numeric_rows':len(nums),'encoding':enc,'raw_microdata_committed':False}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
