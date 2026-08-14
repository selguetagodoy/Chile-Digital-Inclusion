#!/usr/bin/env python3
"""Build March-2026 fixed Internet connections by commune from official SUBTEL XLSX.

The source workbook is downloaded at runtime and not committed. XLSX is read
with Python's standard ZIP/XML libraries. Two official sheets are used:
  - 7.11.CO_FIJAS_COMUNA: total fixed connections
  - 7.11.1.CO_FIJAS_RES_COMUNA: residential fixed connections
"""
from __future__ import annotations

import csv, io, re, unicodedata, urllib.request, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

URL = "https://www.subtel.gob.cl/wp-content/uploads/2026/05/1_SERIES_CONEXIONES_INTERNET_FIJA_MAR26_040526.xlsx"
SHEETS = {
    "total_fixed_connections_2026m03": "7.11.CO_FIJAS_COMUNA",
    "residential_fixed_connections_2026m03": "7.11.1.CO_FIJAS_RES_COMUNA",
}
COMMUNES = Path("geo/commune_codes.csv")
OUT = Path("data/fixed_infrastructure_2026")
OUT.mkdir(parents=True, exist_ok=True)
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL={"rel":"http://schemas.openxmlformats.org/package/2006/relationships"}

ALIASES = {
    "calera": "la calera",
    "aisen": "aysen",
    "coihaique": "coyhaique",
}

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii","ignore").decode("ascii").lower().strip()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return ALIASES.get(s, s)

def col_num(ref: str) -> int:
    m=re.match(r"([A-Z]+)",ref); n=0
    if not m:return 0
    for ch in m.group(1): n=n*26+ord(ch)-64
    return n

def shared(z):
    try: root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:return []
    return ["".join(t.text or "" for t in si.iterfind(".//m:t",NS)) for si in root.findall("m:si",NS)]

def value(c,ss):
    if c.attrib.get("t")=="inlineStr": return "".join(t.text or "" for t in c.iterfind(".//m:t",NS))
    v=c.find("m:v",NS)
    if v is None or v.text is None:return ""
    if c.attrib.get("t")=="s":
        try:return ss[int(v.text)]
        except:return v.text
    return v.text

def sheet_map(z):
    wb=ET.fromstring(z.read("xl/workbook.xml")); rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rm={r.attrib["Id"]:r.attrib["Target"] for r in rels.findall("rel:Relationship",REL)}
    out={}
    for sh in wb.find("m:sheets",NS):
        rid=sh.attrib[f"{{{NS['r']}}}id"]; t=rm[rid]
        out[sh.attrib["name"]] = t.lstrip("/") if t.startswith("/") else "xl/"+t.lstrip("/")
    return out

def row_dict(row,ss):
    return {col_num(c.attrib.get("r","")): value(c,ss) for c in row.findall("m:c",NS)}

def latest_col(root,ss):
    rows={int(r.attrib.get("r","0")):row_dict(r,ss) for r in root.findall(".//m:sheetData/m:row",NS)}
    yrow=rows.get(8,{})
    mrow=rows.get(9,{})
    current_year=None; candidates=[]
    for col in sorted(set(yrow)|set(mrow)):
        y=yrow.get(col,"")
        if re.fullmatch(r"20\d{2}",str(y).strip()): current_year=int(y)
        month=str(mrow.get(col,"")).strip().lower()
        if current_year==2026 and month in {"mar","marzo"}: candidates.append(col)
    if not candidates:
        raise RuntimeError("Could not locate March 2026 column")
    return max(candidates), rows

def extract_sheet(z,ss,path):
    root=ET.fromstring(z.read(path)); target_col, rows=latest_col(root,ss)
    out=[]
    current_region=None
    for rn in sorted(rows):
        if rn < 10: continue
        d=rows[rn]
        region_raw=str(d.get(2,"")).strip()
        if region_raw:
            try:
                current_region=int(float(region_raw))
            except ValueError:
                pass
        commune=str(d.get(3,"")).strip()
        raw=str(d.get(target_col,"")).strip()
        if not commune or not raw or current_region is None: continue
        try: val=int(round(float(raw)))
        except ValueError: continue
        out.append({"region":current_region,"commune_name_source":commune,"value":val,"source_row":rn})
    return out, target_col

def main():
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 Chile-Digital-Inclusion/1.0"})
    with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        ss=shared(z); sm=sheet_map(z); extracted={}; cols={}
        for metric,sname in SHEETS.items():
            extracted[metric],cols[metric]=extract_sheet(z,ss,sm[sname])

    catalog=[]
    with COMMUNES.open(encoding="utf-8") as f:
        for r in csv.DictReader(f): catalog.append(r)
    lookup={(int(r["region"]),norm(r["comuna_nombre"])):r for r in catalog}
    by_name={}
    for r in catalog: by_name.setdefault(norm(r["comuna_nombre"]),[]).append(r)

    by_code={int(r["comuna"]): {**r} for r in catalog}
    unmatched=[]
    for metric, rows in extracted.items():
        for r in rows:
            key=(r["region"],norm(r["commune_name_source"]))
            hit=lookup.get(key)
            if not hit:
                hits=by_name.get(key[1],[])
                hit=hits[0] if len(hits)==1 else None
            if not hit:
                unmatched.append([metric,r["region"],r["commune_name_source"],r["value"],r["source_row"]])
                continue
            by_code[int(hit["comuna"])][metric]=r["value"]

    rows=[]
    for code in sorted(by_code):
        r=by_code[code]
        total=r.get("total_fixed_connections_2026m03")
        residential=r.get("residential_fixed_connections_2026m03")
        share=round(residential/total*100,4) if total and residential is not None else None
        rows.append([r["region"],r["region_nombre"],r["provincia"],r["provincia_nombre"],r["comuna"],r["comuna_nombre"],total,residential,share,"2026-03",URL])

    with (OUT/"commune_fixed_connections_2026_03.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["region","region_nombre","provincia","provincia_nombre","comuna","comuna_nombre","fixed_connections_total","fixed_connections_residential","residential_share_pct","period","source_url"]); w.writerows(rows)
    with (OUT/"source_match_qa.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["metric","source_region","source_commune","value","source_row"]); w.writerows(unmatched)
    with (OUT/"extraction_manifest.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["metric","source_sheet","march_2026_column_number","source_url"])
        for metric,sname in SHEETS.items(): w.writerow([metric,sname,cols[metric],URL])

    matched_total=sum(1 for r in rows if r[6] is not None)
    matched_res=sum(1 for r in rows if r[7] is not None)
    print(f"communes total fixed matched: {matched_total}/346")
    print(f"communes residential fixed matched: {matched_res}/346")
    print(f"unmatched source rows: {len(unmatched)}")
    if matched_total < 340 or matched_res < 340:
        raise SystemExit("Insufficient commune match coverage")

if __name__=="__main__": main()
