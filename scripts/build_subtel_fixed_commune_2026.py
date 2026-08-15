#!/usr/bin/env python3
"""Build March-2026 fixed Internet connections by commune from official SUBTEL XLSX.

The March-2026 workbook contains stale/misaligned commune labels in the 7.11
sheets after the Biobío/Ñuble territorial split. Values themselves are grouped
in 16 regional blocks whose subtotal formulas reconcile exactly. This builder
therefore maps numeric rows inside each formula-defined regional block to the
current official commune catalogue in normalized alphabetical order, validates
row counts and regional subtotals, and publishes row-level mapping provenance.
No missing commune is imputed and no subtotal/total formula cell is used as a
commune observation.
"""
from __future__ import annotations

import csv
import io
import re
import unicodedata
import urllib.request
import zipfile
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
NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
ALIASES = {"calera": "la calera", "aisen": "aysen", "coihaique": "coyhaique", "treguaco": "trehuaco", "til til": "tiltil"}
REGION_CODES = list(range(1, 17))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii").lower().strip()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return ALIASES.get(s, s)


def col_num(ref):
    m = re.match(r"([A-Z]+)", ref)
    n = 0
    if not m:
        return 0
    for ch in m.group(1):
        n = n * 26 + ord(ch) - 64
    return n


def col_letters(n):
    out = ""
    while n:
        n, rem = divmod(n - 1, 26)
        out = chr(65 + rem) + out
    return out


def shared(z):
    try:
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(t.text or "" for t in si.iterfind(".//m:t", NS)) for si in root.findall("m:si", NS)]


def value(c, ss):
    if c.attrib.get("t") == "inlineStr":
        return "".join(t.text or "" for t in c.iterfind(".//m:t", NS))
    v = c.find("m:v", NS)
    if v is None or v.text is None:
        return ""
    if c.attrib.get("t") == "s":
        try:
            return ss[int(v.text)]
        except Exception:
            return v.text
    return v.text


def formula(c):
    f = c.find("m:f", NS)
    return "" if f is None or f.text is None else f.text.strip()


def sheet_map(z):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rm = {r.attrib["Id"]: r.attrib["Target"] for r in rels.findall("rel:Relationship", REL)}
    out = {}
    for sh in wb.find("m:sheets", NS):
        rid = sh.attrib[f"{{{NS['r']}}}id"]
        t = rm[rid]
        out[sh.attrib["name"]] = t.lstrip("/") if t.startswith("/") else "xl/" + t.lstrip("/")
    return out


def parse_rows(root, ss):
    rows = {}
    for row in root.findall(".//m:sheetData/m:row", NS):
        rn = int(row.attrib.get("r", "0"))
        cells = {}
        for c in row.findall("m:c", NS):
            col = col_num(c.attrib.get("r", ""))
            cells[col] = {"value": value(c, ss), "formula": formula(c)}
        rows[rn] = cells
    return rows


def latest_col(rows):
    yrow, mrow = rows.get(8, {}), rows.get(9, {})
    current_year = None
    candidates = []
    for col in sorted(set(yrow) | set(mrow)):
        y = str(yrow.get(col, {}).get("value", "")).strip()
        if re.fullmatch(r"20\d{2}", y):
            current_year = int(y)
        month = str(mrow.get(col, {}).get("value", "")).strip().lower()
        if current_year == 2026 and month in {"mar", "marzo"}:
            candidates.append(col)
    if not candidates:
        raise RuntimeError("Could not locate March 2026 column")
    return max(candidates)


def as_int(raw):
    try:
        return int(round(float(str(raw).strip())))
    except (TypeError, ValueError):
        return None


def regional_formula_blocks(rows, target_col):
    target_letters = col_letters(target_col)
    blocks = []
    pattern = re.compile(rf"^SUM\(\$?{target_letters}\$?(\d+):\$?{target_letters}\$?(\d+)\)$", re.I)
    for rn in sorted(rows):
        cell = rows[rn].get(target_col, {})
        f = str(cell.get("formula", "")).replace(" ", "")
        m = pattern.match(f)
        if not m:
            continue
        start, end = int(m.group(1)), int(m.group(2))
        blocks.append({"subtotal_row": rn, "start_row": start, "end_row": end, "subtotal": as_int(cell.get("value"))})
    if len(blocks) != 16:
        raise RuntimeError(f"Expected 16 regional subtotal formula blocks, found {len(blocks)}")
    for region, block in zip(REGION_CODES, blocks):
        block["region"] = region
    return blocks


def build_metric(rows, target_col, catalogue_by_region, metric):
    mapped = {}
    alignment = []
    row_provenance = []
    issues = []

    for block in regional_formula_blocks(rows, target_col):
        region = block["region"]
        communes = catalogue_by_region[region]
        observations = []
        for rn in range(block["start_row"], block["end_row"] + 1):
            cell = rows.get(rn, {}).get(target_col, {})
            if cell.get("formula"):
                continue
            v = as_int(cell.get("value"))
            if v is None:
                continue
            source_label = str(rows.get(rn, {}).get(3, {}).get("value", "")).strip()
            observations.append((rn, source_label, v))

        count_ok = len(observations) == len(communes)
        value_sum = sum(v for _, _, v in observations)
        subtotal = block["subtotal"]
        subtotal_ok = subtotal is not None and value_sum == subtotal
        label_matches = 0

        if count_ok:
            for commune, (rn, source_label, v) in zip(communes, observations):
                code = int(commune["comuna"])
                mapped[code] = v
                if norm(source_label) == norm(commune["comuna_nombre"]):
                    label_matches += 1
                row_provenance.append(
                    {
                        "metric": metric,
                        "region": region,
                        "source_row": rn,
                        "source_commune_label": source_label,
                        "mapped_commune": code,
                        "mapped_commune_name": commune["comuna_nombre"],
                        "value": v,
                        "mapping_method": "regional_formula_block_order",
                        "block_start_row": block["start_row"],
                        "block_end_row": block["end_row"],
                        "regional_subtotal_row": block["subtotal_row"],
                    }
                )

        alignment.append(
            {
                "metric": metric,
                "region": region,
                "block_start_row": block["start_row"],
                "block_end_row": block["end_row"],
                "regional_subtotal_row": block["subtotal_row"],
                "numeric_commune_rows": len(observations),
                "catalogue_communes": len(communes),
                "regional_subtotal": subtotal,
                "mapped_value_sum": value_sum,
                "subtotal_delta": "" if subtotal is None else value_sum - subtotal,
                "source_labels_matching_mapped_names": label_matches,
                "count_status": "pass" if count_ok else "fail",
                "subtotal_status": "pass" if subtotal_ok else "fail",
            }
        )
        if not count_ok or not subtotal_ok:
            issues.append(
                [metric, region, block["start_row"], block["end_row"], len(observations), len(communes), subtotal, value_sum]
            )

    return mapped, alignment, row_provenance, issues


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 Chile-Digital-Inclusion/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = r.read()

    with COMMUNES.open(encoding="utf-8") as f:
        catalogue = list(csv.DictReader(f))
    catalogue_by_region = {}
    for region in REGION_CODES:
        rows = [r for r in catalogue if int(r["region"]) == region]
        catalogue_by_region[region] = sorted(rows, key=lambda r: norm(r["comuna_nombre"]))

    all_alignment = []
    all_provenance = []
    all_issues = []
    metric_maps = {}
    cols = {}

    with zipfile.ZipFile(io.BytesIO(data)) as z:
        ss = shared(z)
        sm = sheet_map(z)
        for metric, sheet_name in SHEETS.items():
            root = ET.fromstring(z.read(sm[sheet_name]))
            rows = parse_rows(root, ss)
            target_col = latest_col(rows)
            cols[metric] = target_col
            mapped, alignment, provenance, issues = build_metric(rows, target_col, catalogue_by_region, metric)
            metric_maps[metric] = mapped
            all_alignment.extend(alignment)
            all_provenance.extend(provenance)
            all_issues.extend(issues)

    if all_issues:
        raise RuntimeError(f"Regional formula-block reconciliation failed: {all_issues}")

    rows_out = []
    missing = []
    by_code = {int(r["comuna"]): r for r in catalogue}
    for code in sorted(by_code):
        r = by_code[code]
        total = metric_maps["total_fixed_connections_2026m03"].get(code)
        residential = metric_maps["residential_fixed_connections_2026m03"].get(code)
        share = round(residential / total * 100, 4) if total and residential is not None else None
        status = "reported" if total is not None and residential is not None else "source_not_reported"
        rows_out.append(
            [
                r["region"], r["region_nombre"], r["provincia"], r["provincia_nombre"], r["comuna"], r["comuna_nombre"],
                total, residential, share, status, "regional_formula_block_order", "2026-03", URL,
            ]
        )
        if status != "reported":
            missing.append([r["region"], r["region_nombre"], r["comuna"], r["comuna_nombre"], total, residential])

    with (OUT / "commune_fixed_connections_2026_03.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "region", "region_nombre", "provincia", "provincia_nombre", "comuna", "comuna_nombre",
            "fixed_connections_total", "fixed_connections_residential", "residential_share_pct", "source_status",
            "source_mapping_method", "period", "source_url",
        ])
        w.writerows(rows_out)

    with (OUT / "source_match_qa.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "region", "block_start_row", "block_end_row", "numeric_rows", "catalogue_communes", "regional_subtotal", "mapped_value_sum"])
        w.writerows(all_issues)

    with (OUT / "source_not_reported_communes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["region", "region_nombre", "comuna", "comuna_nombre", "fixed_connections_total", "fixed_connections_residential"])
        w.writerows(missing)

    with (OUT / "source_alignment_qa.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "metric", "region", "block_start_row", "block_end_row", "regional_subtotal_row", "numeric_commune_rows",
            "catalogue_communes", "regional_subtotal", "mapped_value_sum", "subtotal_delta",
            "source_labels_matching_mapped_names", "count_status", "subtotal_status",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_alignment)

    with (OUT / "source_row_mapping_2026_03.csv").open("w", newline="", encoding="utf-8") as f:
        fields = [
            "metric", "region", "source_row", "source_commune_label", "mapped_commune", "mapped_commune_name", "value",
            "mapping_method", "block_start_row", "block_end_row", "regional_subtotal_row",
        ]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_provenance)

    with (OUT / "extraction_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "source_sheet", "march_2026_column_number", "mapping_method", "source_url"])
        for metric, sheet_name in SHEETS.items():
            w.writerow([metric, sheet_name, cols[metric], "regional_formula_block_order_with_subtotal_reconciliation", URL])

    mt = sum(1 for r in rows_out if r[6] is not None)
    mr = sum(1 for r in rows_out if r[7] is not None)
    print(f"communes total fixed reported: {mt}/346")
    print(f"communes residential fixed reported: {mr}/346")
    print(f"catalogue communes not reported: {len(missing)}")
    print("regional alignment checks:", len(all_alignment), "all pass")
    if mt != 346 or mr != 346 or missing:
        raise SystemExit("Formula-block reconstruction did not recover all 346 communes")


if __name__ == "__main__":
    main()
