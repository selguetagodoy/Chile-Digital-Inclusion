#!/usr/bin/env python3
"""Inspect the official SUBTEL fixed-connections commune sheet for a robust parser."""
from __future__ import annotations
import csv, io, re, urllib.request, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

URL = "https://www.subtel.gob.cl/wp-content/uploads/2026/05/1_SERIES_CONEXIONES_INTERNET_FIJA_MAR26_040526.xlsx"
TARGET = "7.11.CO_FIJAS_COMUNA"
OUT = Path("data/subtel_sector_2026/xlsx_profile/fixed_commune_sheet_structure.csv")
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL={"rel":"http://schemas.openxmlformats.org/package/2006/relationships"}

def shared(z):
    try: root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError: return []
    return ["".join(t.text or "" for t in si.iterfind(".//m:t",NS)) for si in root.findall("m:si",NS)]

def val(c, ss):
    if c.attrib.get("t")=="inlineStr": return "".join(x.text or "" for x in c.iterfind(".//m:t",NS))
    v=c.find("m:v",NS)
    if v is None or v.text is None: return ""
    if c.attrib.get("t")=="s":
        try:return ss[int(v.text)]
        except:return v.text
    return v.text

def target_path(z):
    wb=ET.fromstring(z.read("xl/workbook.xml")); rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rm={r.attrib["Id"]:r.attrib["Target"] for r in rels.findall("rel:Relationship",REL)}
    for sh in wb.find("m:sheets",NS):
        if sh.attrib["name"]==TARGET:
            rid=sh.attrib[f"{{{NS['r']}}}id"]; t=rm[rid]
            return t.lstrip("/") if t.startswith("/") else "xl/"+t.lstrip("/")
    raise RuntimeError("target sheet not found")

def main():
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 Chile-Digital-Inclusion/1.0"})
    with urllib.request.urlopen(req,timeout=90) as r:data=r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        ss=shared(z); root=ET.fromstring(z.read(target_path(z)))
        rows=root.findall(".//m:sheetData/m:row",NS)
        wanted=set(range(1,81)) | set(range(max(1,len(rows)-25),len(rows)+1))
        out=[]
        for row in rows:
            rn=int(row.attrib.get("r","0") or 0)
            if rn not in wanted: continue
            for c in row.findall("m:c",NS):
                v=val(c,ss)
                if v!="": out.append([rn,c.attrib.get("r",""),v])
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open("w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["row","cell","value"]); w.writerows(out)
    print(f"wrote {len(out)} non-empty cells")
if __name__=="__main__": main()
