#!/usr/bin/env python3
"""Recalculate Data Package sizes/hashes after refreshing derived data."""
import hashlib
import json
from pathlib import Path
p = Path("datapackage.json")
package = json.loads(p.read_text(encoding="utf-8"))
for r in package["resources"]:
    if r["name"] == "ookla-national-2026q2":
        r["name"] = "ookla-national-2026q3"
        r["path"] = "data/ookla/chile_2026q3_summary.csv"
    elif r["name"] == "ookla-communal-2026q2":
        r["name"] = "ookla-communal-2026q3"
        r["path"] = "data/ookla/territorial/chile_2026q3_communes.csv"
    raw = Path(r["path"]).read_bytes()
    r["bytes"] = len(raw)
    r["git_blob_sha"] = hashlib.sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
p.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Data Package hashes current")
