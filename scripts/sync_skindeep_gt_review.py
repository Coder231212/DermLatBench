#!/usr/bin/env python3
"""Reconcile completed SkinDeep annotation review labels into metadata-only GT.

Preserves earlier explicit manual corrections; does not touch image files.
Run from repository root: python scripts/sync_skindeep_gt_review.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASKS = ROOT / "data/skindeep_mask_annotations_export.json"
GT_PATHS = [
    ROOT / "data/skindeep_metadata.csv",
    ROOT / "data/dermlatbench_metadata.csv",
]
AUDIT = ROOT / "docs/skindeep_gt_annotation_reconciliation_20261120.csv"
REPORT = ROOT / "docs/SKINDEEP_GT_RECONCILIATION_20261120.md"
LOCKED = {"DLB_00012001": "LEFT", "DLB_00012096": "RIGHT"}
ALLOWED = {"LEFT", "RIGHT", "BILATERAL_OR_MIDLINE", "UNABLE_TO_DETERMINE"}
SOURCE = "SKINDEEP_MASK_ANNOTATION_REVIEW_20261008"

def read_csv(path):
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)

def main():
    annotations = json.loads(MASKS.read_text(encoding="utf-8"))
    assert len(annotations) == 542, "Expected 542 SkinDeep annotation records"
    assert len({r["image_id"] for r in annotations}) == 542, "Duplicate annotation IDs"
    assert all(r.get("annotation_complete") == "YES" for r in annotations), "Incomplete annotation export"
    annotations_by_id = {r["image_id"]: r for r in annotations}

    fields, skindeep = read_csv(GT_PATHS[0])
    assert len(skindeep) == 542
    by_id = {row["image_id"]: row for row in skindeep}
    assert len(by_id) == 542
    changes, exceptions = {}, {}
    for image_id, annotation in annotations_by_id.items():
        assert image_id in by_id, f"Missing SkinDeep GT: {image_id}"
        before = by_id[image_id]["final_patient_laterality"]
        after = annotation["final_patient_laterality"]
        assert after in ALLOWED, (image_id, after)
        if image_id in LOCKED:
            assert before == LOCKED[image_id], f"Unexpected manual GT: {image_id}"
            if before != after:
                exceptions[image_id] = (before, after)
        elif before != after:
            changes[image_id] = {
                "previous_laterality": before,
                "updated_laterality": after,
                "previous_source": by_id[image_id]["final_label_source"],
                "annotation_saved_at": annotation["saved_at"],
            }
    assert len(changes) == 20, f"Expected 20 revisions; found {len(changes)}"
    assert set(exceptions) == set(LOCKED), f"Manual-correction conflicts changed: {exceptions}"

    output_rows = []
    for path in GT_PATHS:
        fieldnames, rows = read_csv(path)
        assert len(rows) == (542 if "skindeep_metadata" in path.name else 12541)
        seen = set()
        for row in rows:
            image_id = row["image_id"]
            if image_id not in changes:
                continue
            info = changes[image_id]
            assert row["final_patient_laterality"] == info["previous_laterality"], image_id
            new_side = info["updated_laterality"]
            row["final_patient_laterality"] = new_side
            row["final_label_source"] = SOURCE
            old_note = row.get("final_resolution_note", "")
            note = (
                f"Mask annotation review ({info['annotation_saved_at']}): "
                f"{info['previous_laterality']} -> {new_side}; applied 2026-11-20."
            )
            row["final_resolution_note"] = " | ".join(x for x in (old_note, note) if x)
            row["final_lr_probe_include"] = "YES" if new_side in ("LEFT", "RIGHT") else "NO"
            row["final_laterality_determinable"] = "YES" if new_side in ("LEFT", "RIGHT") else "NO"
            row["final_gt_status"] = "FINAL"
            row["final_gt_include"] = "YES"
            seen.add(image_id)
        assert seen == set(changes), f"Not all changes applied in {path}"
        output_rows.append((path, fieldnames, rows))

    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "image_id", "previous_laterality", "updated_laterality",
            "previous_source", "annotation_saved_at"
        ])
        writer.writeheader()
        for image_id in sorted(changes):
            writer.writerow({"image_id": image_id, **changes[image_id]})

    REPORT.write_text(
        "# SkinDeep GT reconciliation (2026-11-20)\n\n"
        "20 revised laterality labels from the completed SkinDeep annotation review "
        "were synchronized into both SkinDeep and full DermLatBench ground-truth files. "
        "See the CSV in this folder for a row-level audit. Original human votes and "
        "consensus fields are unchanged.\n\n"
        "Two newer explicit manual corrections take precedence and remain unchanged:\n"
        "- DLB_00012001: LEFT (older export: RIGHT)\n"
        "- DLB_00012096: RIGHT (older export: UNABLE_TO_DETERMINE)\n\n"
        "Updated source label: `" + SOURCE + "`. These reviewer annotations "
        "must not be mistaken for independent three-rater consensus. "
        "Recompute manuscript model metrics after this GT revision. "
        "No source, masked, or cropped images are included.\n",
        encoding="utf-8"
    )
    for path, fieldnames, rows in output_rows:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    print(f"Updated {len(changes)} SkinDeep images across {len(GT_PATHS)} GT files")
    print("Manual locks preserved:", exceptions)
    print("Changes by new label:", dict(Counter(x["updated_laterality"] for x in changes.values())))

if __name__ == "__main__":
    main()
