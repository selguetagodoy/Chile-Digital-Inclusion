from pathlib import Path
import csv

DATA = Path(__file__).resolve().parents[1] / "data"

for path in sorted(DATA.glob("*.csv")):
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    print(f"{path.name}: {max(len(rows)-1,0)} records")
