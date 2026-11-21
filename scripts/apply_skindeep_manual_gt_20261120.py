#!/usr/bin/env python3
"""Apply user-confirmed GT corrections across the full and SkinDeep metadata.

This does not change original evaluator votes, consensus, or image files.
Idempotent: running twice does not duplicate audit notes.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ROOT / "data" / "skindeep_metadata.csv",
    ROOT / "data" / "dermlatbench_metadata.csv",
)
CORRECTIONS = {
    "DLB_00012001": {"final_patient_laterality": "RIGHT", "final_body_region": "finger"},
    "DLB_00012096": {"final_patient_laterality": "RIGHT", "final_body_region": "lower_leg"},
}
AUDIT = ROOT / "docs" / "SKINDEEP_GT_MANUAL_CORRECTIONS_20261120.md"
NOTE = "User-confirmed correction (2026-11-20): laterality RIGHT."
SOURCE = "MANUAL_USER_CORRECTION_20261120"


def main() -> None:
    results = []
    for path in FILES:
        with path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            assert fields is not None
            rows = list(reader)

        seen = set()
        for row in rows:
            image_id = row["image_id"].upper()
            if image_id not in CORRECTIONS:
                continue
            assert image_id not in seen, f"Duplicate image_id: {image_id}"
            seen.add(image_id)
            correction = CORRECTIONS[image_id]
            before = row["final_patient_laterality"]
            assert before in {"LEFT", "RIGHT"}, (image_id, before)
            row.update(correction)
            row["final_label_source"] = SOURCE
            row["final_gt_status"] = "FINAL"
            row["final_gt_include"] = "YES"
            row["final_lr_probe_include"] = "YES"
            if "final_laterality_determinable" in row:
                row["final_laterality_determinable"] = "YES"
            row["final_resolution_note"] = (
                row.get("final_resolution_note", "")
                if NOTE in row.get("final_resolution_note", "")
                else " | ".join(filter(None, [row.get("final_resolution_note", ""), NOTE]))
            )
            results.append((path.name, image_id, before, "RIGHT"))

        assert seen == set(CORRECTIONS), f"Missing cases in {path}: {set(CORRECTIONS) - seen}"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    AUDIT.write_text(
        "# SkinDeep manual ground-truth confirmation, 2026-11-20\n\n"
        "User-confirmed values:\n\n"
        "- `DLB_00012001`: RIGHT, body region `finger`. "
        "Overrides the preceding LEFT GT record.\n"
        "- `DLB_00012096`: RIGHT, body region `lower_leg`. "
        "Retains the existing RIGHT GT record.\n\n"
        "Changes synchronized to `data/skindeep_metadata.csv` and "
        "`data/dermlatbench_metadata.csv`. Original independent human votes, "
        "consensus, and source images remain unchanged. "
        "Recompute analyses using the new GT revision.\n",
        encoding="utf-8",
    )
    for r in results:
        print(*r, sep=" | ")


if __name__ == "__main__":
    main()
