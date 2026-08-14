#!/usr/bin/env python3
"""Profile official SUBTEL XLSX sector files without persisting the source workbooks.

Uses only Python standard library to read XLSX ZIP/XML structures. The source
files are downloaded at runtime and deleted after profiling. Outputs are CSV
metadata and sampled cell values for reproducibility/auditing.
"""
from __future__ import annotations

import csv
import io
import re
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

OUT = Path("data/subtel_sector_2026/xlsx_profile")
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = [
    ("fixed_connections", "https://www.subtel.gob.cl/wp-content/uploads/2026/05/1_SERIES_CONEXIONES_INTERNET_FIJA_MAR26_040526.xlsx"),
    ("mobile_connections", "https://www.subtel.gob.cl/wp-content/uploads/2026/05/2_SERIES_CONEXIONES_INTERNET_MO%CC%81VIL-MAR26-040526.xlsx"),
    ("mobile_traffic", "https://www.subtel.gob.cl/wp-content/uploads/2026/05/3_SERIES_TRAFICO_DATOS_MOVILES-MAR26-040526.xlsx"),
    ("fixed_traffic", "https://www.subtel.gob.cl/wp-content/uploads/2026/05/3_SERIES_TRAFICO_DATOS_FIJOS-MAR26-040526.xlsx"),
]

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL_NS = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}


def col_num(ref: str) -> int:
    m = re.match(r"([A-Z]+)", ref)
    if not m:
        return 0
    n = 0
    for ch in m.group(1):
        n = n * 26 + ord(ch) - 64
    return n


def shared_strings(z: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    out = []
    for si in root.findall("m:si", NS):
        out.append("".join(t.text or "" for t in si.iterfind(".//m:t", NS)))
    return out


def sheet_paths(z: zipfile.ZipFile):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap = {r.attrib["Id"]: r.attrib["Target"] for r in rels.findall("rel:Relationship", REL_NS)}
    result = []
    for sh in wb.find("m:sheets", NS):
        rid = sh.attrib[f"{{{NS['r']}}}id"]
        target = relmap[rid]
        if target.startswith("/"):
            path = target.lstrip("/")
        else:
            path = "xl/" + target.lstrip("/")
        result.append((sh.attrib["name"], path))
    return result


def cell_value(c, strings):
    t = c.attrib.get("t")
    if t == "inlineStr":
        return "".join(x.text or "" for x in c.iterfind(".//m:t", NS))
    v = c.find("m:v", NS)
    if v is None or v.text is None:
        return ""
    if t == "s":
        try:
            return strings[int(v.text)]
        except Exception:
            return v.text
    return v.text


def profile_one(source_id: str, url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Chile-Digital-Inclusion/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        strings = shared_strings(z)
        sheet_rows = []
        sample_rows = []
        for sheet_name, path in sheet_paths(z):
            root = ET.fromstring(z.read(path))
            dim = root.find("m:dimension", NS)
            dimension = dim.attrib.get("ref", "") if dim is not None else ""
            cells = root.findall(".//m:sheetData/m:row/m:c", NS)
            max_row = 0
            max_col = 0
            for c in cells:
                ref = c.attrib.get("r", "")
                rm = re.search(r"(\d+)$", ref)
                if rm:
                    max_row = max(max_row, int(rm.group(1)))
                max_col = max(max_col, col_num(ref))
            sheet_rows.append([source_id, url, sheet_name, path, dimension, max_row, max_col, len(cells), len(data)])

            for row in root.findall(".//m:sheetData/m:row", NS)[:25]:
                rnum = int(row.attrib.get("r", "0") or 0)
                vals = []
                for c in row.findall("m:c", NS)[:30]:
                    vals.append(f"{c.attrib.get('r','')}={cell_value(c, strings)}")
                if vals:
                    sample_rows.append([source_id, sheet_name, rnum, " | ".join(vals)])
        return sheet_rows, sample_rows


def main():
    all_sheets, all_samples = [], []
    errors = []
    for sid, url in SOURCES:
        try:
            sheets, samples = profile_one(sid, url)
            all_sheets.extend(sheets)
            all_samples.extend(samples)
            print(f"{sid}: {len(sheets)} sheets")
        except Exception as e:
            errors.append([sid, url, type(e).__name__, str(e)])
            print(f"ERROR {sid}: {e}")

    with (OUT / "workbook_catalog.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_id","source_url","sheet_name","xml_path","dimension","max_row","max_col","cell_count","download_bytes"])
        w.writerows(all_sheets)
    with (OUT / "sheet_samples.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_id","sheet_name","row_number","sample_cells"])
        w.writerows(all_samples)
    with (OUT / "download_errors.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["source_id","source_url","error_type","error"])
        w.writerows(errors)
    if errors:
        raise SystemExit(f"{len(errors)} source workbook(s) failed")


if __name__ == "__main__":
    main()
