#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTOR = ROOT / "datapackage.json"


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def main() -> int:
    failures: list[str] = []

    if not DESCRIPTOR.exists():
        print("ERROR: datapackage.json missing")
        return 2

    try:
        package = json.loads(DESCRIPTOR.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid datapackage.json — {exc}")
        return 2

    if package.get("profile") != "data-package":
        failures.append("profile must be 'data-package'")

    resources = package.get("resources", [])
    if not resources:
        failures.append("no resources declared")

    names: set[str] = set()
    paths: set[str] = set()

    for resource in resources:
        name = resource.get("name")
        rel = resource.get("path")
        if not name or not rel:
            failures.append("resource missing name/path")
            continue

        if name in names:
            failures.append(f"duplicate resource name: {name}")
        names.add(name)

        if rel in paths:
            failures.append(f"duplicate resource path: {rel}")
        paths.add(rel)

        target = ROOT / rel
        if not target.exists() or not target.is_file():
            failures.append(f"resource missing: {rel}")
            continue

        data = target.read_bytes()
        actual_size = len(data)
        actual_sha = git_blob_sha(data)
        declared_size = resource.get("bytes")
        declared_sha = resource.get("git_blob_sha")

        if declared_size != actual_size:
            failures.append(
                f"size drift: {rel} — declared {declared_size}, actual {actual_size}"
            )
        if declared_sha != actual_sha:
            failures.append(
                f"blob drift: {rel} — declared {declared_sha}, actual {actual_sha}"
            )

        suffix = target.suffix.lower()
        declared_format = (resource.get("format") or "").lower()
        if suffix == ".csv" and declared_format != "csv":
            failures.append(f"format mismatch: {rel} should declare csv")
        if suffix == ".json" and declared_format not in {"json", "geojson"}:
            failures.append(f"format mismatch: {rel} should declare json")
        if suffix == ".geojson" and declared_format != "geojson":
            failures.append(f"format mismatch: {rel} should declare geojson")

        print(
            f"OK {name}: {rel} · {actual_size} bytes · {actual_sha}"
        )

    print(
        f"\nData Package integrity: {len(resources)} resources · "
        f"{len(failures)} failures"
    )
    if failures:
        for failure in failures:
            print("ERROR:", failure)
        return 1

    print("OK: declared resources match the current repository files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
