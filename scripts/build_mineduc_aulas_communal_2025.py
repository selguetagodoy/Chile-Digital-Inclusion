from __future__ import annotations

import csv
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import requests

DIRECTORY_URL='https://datosabiertos.mineduc.cl/wp-content/uploads/2025/11/Directorio-Oficial-EE-2025.rar'
AULAS=Path('data/education_connectivity_2026/aulas_conectadas_2025_establishments.csv')
COMMUNES=Path('geo/commune_codes.csv')
OUT_ENRICHED=Path('data/education_connectivity_2026/aulas_conectadas_2025_establishments_enriched.csv')
OUT_COMMUNES=Path('data/education_connectivity_2026/aulas_conectadas_2025_commune_summary.csv')
OUT_QA=Path('data/education_connectivity_2026/aulas_conectadas_2025_crosswalk_qa.csv')


def clean(v):
    return '' if v is None else str(v).strip()


def norm_intish(v):
    s=clean(v)
    if not s:
        return ''
    try:
        return str(int(float(s)))
    except ValueError:
        return s


def norm_rbd(v):
    s=clean(v).upper()
    if '-' in s:
        s=s.split('-',1)[0]
    return norm_intish(s)


def download_directory() -> bytes:
    r=requests.get(DIRECTORY_URL,timeout=180,allow_redirects=True)
    r.raise_for_status()
    if len(r.content) < 100000:
        raise RuntimeError(f'Official directory archive unexpectedly small: {len(r.content)} bytes')
    return r.content


def extract_archive(body: bytes, root: Path) -> Path:
    archive=root/'directory.rar'; archive.write_bytes(body)
    extract=root/'extract'; extract.mkdir()
    cmds=[
        ['unar','-quiet','-force-overwrite','-output-directory',str(extract),str(archive)],
        ['7z','x','-y',f'-o{extract}',str(archive)],
    ]
    errors=[]
    for cmd in cmds:
        proc=subprocess.run(cmd,capture_output=True,text=True)
        csvs=list(extract.rglob('*.csv'))
        if proc.returncode==0 and csvs:
            preferred=[p for p in csvs if 'Directorio_Oficial_EE_2025' in p.name]
            return preferred[0] if preferred else csvs[0]
        errors.append(f'{cmd[0]} rc={proc.returncode} {proc.stdout[-200:]} {proc.stderr[-200:]}')
    raise RuntimeError('Could not extract directory: '+' | '.join(errors))


def read_directory(path: Path):
    with path.open(encoding='utf-8-sig',newline='') as fh:
        sample=fh.read(8192); fh.seek(0)
        try:
            dialect=csv.Sniffer().sniff(sample,delimiters=';,|\t,')
        except csv.Error:
            dialect=csv.excel
        reader=csv.DictReader(fh,dialect=dialect)
        required={'RBD','NOM_RBD','COD_REG_RBD','NOM_REG_RBD_A','COD_COM_RBD','NOM_COM_RBD','RURAL_RBD','LATITUD','LONGITUD','COD_DEPE','COD_DEPE2','MAT_TOTAL','ESTADO_ESTAB','CONVENIO_PIE','PACE'}
        missing=required-set(reader.fieldnames or [])
        if missing:
            raise RuntimeError(f'Official directory missing columns: {sorted(missing)}')
        rows=[]
        for r in reader:
            rbd=norm_rbd(r['RBD'])
            if rbd:
                rows.append({
                    'rbd':rbd,
                    'official_establishment_name':clean(r['NOM_RBD']),
                    'region_code':norm_intish(r['COD_REG_RBD']),
                    'region_name':clean(r['NOM_REG_RBD_A']),
                    'commune_code':norm_intish(r['COD_COM_RBD']),
                    'commune_name':clean(r['NOM_COM_RBD']),
                    'rural_rbd':norm_intish(r['RURAL_RBD']),
                    'latitude':clean(r['LATITUD']),
                    'longitude':clean(r['LONGITUD']),
                    'dependency_code':norm_intish(r['COD_DEPE']),
                    'dependency_group_code':norm_intish(r['COD_DEPE2']),
                    'enrollment_total':norm_intish(r['MAT_TOTAL']),
                    'establishment_state':clean(r['ESTADO_ESTAB']),
                    'pie_agreement':norm_intish(r['CONVENIO_PIE']),
                    'pace':norm_intish(r['PACE']),
                })
    return rows


def int_or_zero(v):
    try:
        return int(float(clean(v)))
    except (TypeError,ValueError):
        return 0


def main():
    OUT_ENRICHED.parent.mkdir(parents=True,exist_ok=True)
    with AULAS.open(encoding='utf-8-sig',newline='') as fh:
        program=list(csv.DictReader(fh))
    with COMMUNES.open(encoding='utf-8-sig',newline='') as fh:
        commune_catalog=list(csv.DictReader(fh))

    with tempfile.TemporaryDirectory() as td:
        directory_csv=extract_archive(download_directory(),Path(td))
        directory=read_directory(directory_csv)

    counts=Counter(r['rbd'] for r in directory)
    duplicate_directory={k:v for k,v in counts.items() if v>1}
    directory_by_rbd={r['rbd']:r for r in directory}

    enriched=[]; unmatched=[]
    for p in program:
        rbd=norm_rbd(p['rbd'])
        d=directory_by_rbd.get(rbd)
        if d is None:
            unmatched.append(rbd)
            d={k:'' for k in ['official_establishment_name','region_code','region_name','commune_code','commune_name','rural_rbd','latitude','longitude','dependency_code','dependency_group_code','enrollment_total','establishment_state','pie_agreement','pace']}
        row={
            'selection_group':p['selection_group'],
            'rbd':rbd,
            'program_establishment_name':p['establishment_name'],
            **d,
            'sponsor_name':p['sponsor_name'],
            'project':p['project'],
            'selection_status':p['selection_status'],
            'waitlist_position':p['waitlist_position'],
            'program_source':p['source_spreadsheet'],
            'directory_source':DIRECTORY_URL,
        }
        enriched.append(row)

    summary=defaultdict(lambda:{'selected':0,'waitlist':0,'selected_rural':0,'selected_enrollment':0,'selected_with_coordinates':0})
    for r in enriched:
        code=r['commune_code']
        if not code:
            continue
        s=summary[code]
        if r['selection_group']=='selected':
            s['selected']+=1
            if r['rural_rbd']=='1': s['selected_rural']+=1
            s['selected_enrollment']+=int_or_zero(r['enrollment_total'])
            if clean(r['latitude']) and clean(r['longitude']): s['selected_with_coordinates']+=1
        elif r['selection_group']=='waitlist':
            s['waitlist']+=1

    commune_rows=[]
    for c in commune_catalog:
        code=norm_intish(c['comuna'])
        s=summary[code]
        commune_rows.append({
            'comuna':code,
            'comuna_nombre':c['comuna_nombre'],
            'provincia':c['provincia'],
            'provincia_nombre':c['provincia_nombre'],
            'region':c['region'],
            'region_nombre':c['region_nombre'],
            'mineduc_aulas_selected_establishments_2025':s['selected'],
            'mineduc_aulas_waitlist_establishments_2025':s['waitlist'],
            'mineduc_aulas_selected_rural_establishments_2025':s['selected_rural'],
            'mineduc_aulas_selected_enrollment_2025':s['selected_enrollment'],
            'mineduc_aulas_selected_with_coordinates_2025':s['selected_with_coordinates'],
        })

    with OUT_ENRICHED.open('w',encoding='utf-8',newline='') as fh:
        fields=list(enriched[0].keys()); w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(enriched)
    with OUT_COMMUNES.open('w',encoding='utf-8',newline='') as fh:
        fields=list(commune_rows[0].keys()); w=csv.DictWriter(fh,fieldnames=fields); w.writeheader(); w.writerows(commune_rows)

    selected=sum(r['selection_group']=='selected' for r in enriched)
    waitlist=sum(r['selection_group']=='waitlist' for r in enriched)
    matched=len(enriched)-len(unmatched)
    selected_communes=sum(r['mineduc_aulas_selected_establishments_2025']>0 for r in commune_rows)
    qa=[
        ('program_records',len(program),'793'),
        ('program_unique_rbd',len({norm_rbd(r['rbd']) for r in program}),'793'),
        ('selected_records',selected,'700'),
        ('waitlist_records',waitlist,'93'),
        ('directory_records',len(directory),'official directory rows'),
        ('directory_unique_rbd',len(counts),'should equal directory records unless duplicate RBD'),
        ('directory_duplicate_rbd',len(duplicate_directory),'0 expected'),
        ('program_rbd_matched',matched,'matched to official directory'),
        ('program_rbd_unmatched',len(unmatched),'0 expected'),
        ('program_rbd_match_pct',round(matched/len(enriched)*100,4) if enriched else 0,'100 expected'),
        ('commune_summary_rows',len(commune_rows),'346'),
        ('communes_with_selected_establishments',selected_communes,'descriptive'),
        ('selected_establishments_sum_communes',sum(r['mineduc_aulas_selected_establishments_2025'] for r in commune_rows),'700 expected if full match'),
        ('waitlist_establishments_sum_communes',sum(r['mineduc_aulas_waitlist_establishments_2025'] for r in commune_rows),'93 expected if full match'),
    ]
    with OUT_QA.open('w',encoding='utf-8',newline='') as fh:
        w=csv.DictWriter(fh,fieldnames=['metric','value','expectation']); w.writeheader();
        for metric,value,expectation in qa: w.writerow({'metric':metric,'value':value,'expectation':expectation})

    if unmatched:
        print('UNMATCHED',unmatched)
    print('program',len(program),'directory',len(directory),'matched',matched,'unmatched',len(unmatched),'selected_communes',selected_communes)

if __name__=='__main__':
    main()
