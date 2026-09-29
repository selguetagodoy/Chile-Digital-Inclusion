#!/usr/bin/env python3
"""Build the published SUBTEL 2025 daily Internet-use-by-age table."""

from __future__ import annotations

import csv
from pathlib import Path

OUT = Path("data/subtel_longitudinal/subtel_internet_use_by_age_2025.csv")
SOURCE_URL = (
    "https://www.subtel.gob.cl/wp-content/uploads/2026/02/"
    "Informe-Final-Acceso-y-Uso-Internet-2025_03.pdf"
)
SOURCE_PAGE = 46
ROWS = [
    ("16-29", 1, 96.9),
    ("30-44", 2, 97.0),
    ("45-59", 3, 90.9),
    ("60+", 4, 74.4),
]
FIELDS = [
    "reference_year", "survey_wave", "age_group", "age_order",
    "daily_use_pct", "reference_window", "question_id", "indicator",
    "source_page", "source_url",
]


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "reference_year": 2025,
            "survey_wave": "XII",
            "age_group": age_group,
            "age_order": order,
            "daily_use_pct": value,
            "reference_window": "last_3_months",
            "question_id": "Q10",
            "indicator": "Uso de Internet todos los días",
            "source_page": SOURCE_PAGE,
            "source_url": SOURCE_URL,
        }
        for age_group, order, value in ROWS
    ]
    if len({row["age_group"] for row in rows}) != 4:
        raise RuntimeError("Age groups must be unique")
    if any(not 0 <= row["daily_use_pct"] <= 100 for row in rows):
        raise RuntimeError("Daily-use percentages must be between 0 and 100")

    with OUT.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print("subtel_internet_use_by_age_2025 rows", len(rows))
    print("30-44_vs_60plus_gap_pp", round(rows[1]["daily_use_pct"] - rows[3]["daily_use_pct"], 1))


if __name__ == "__main__":
    main()
