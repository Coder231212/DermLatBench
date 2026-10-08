#!/usr/bin/env python3
import argparse
from pathlib import Path
import pandas as pd
from PIL import Image
from tqdm import tqdm
from dermlatbench.periorbital_crop import BBox, crop_pil, infer_periorbital_boxes_facemesh

def crop_from_bbox_csv(image_dir: Path, bbox_csv: Path, out_dir: Path, margin: float):
    df = pd.read_csv(bbox_csv); required = {"image_id","x_min","y_min","x_max","y_max"}
    missing = required - set(df.columns)
    if missing: raise ValueError(f"bbox_csv missing columns: {sorted(missing)}")
    exts = [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"]
    for _, row in tqdm(df.iterrows(), total=len(df)):
        image_id = str(row["image_id"]); src = None
        for ext in exts:
            c = image_dir/f"{image_id}{ext}"
            if c.exists(): src = c; break
        if src is None:
            matches = [m for m in image_dir.rglob(f"{image_id}.*") if m.suffix.lower() in exts]
            if matches: src = matches[0]
        if src is None: print(f"Missing source image: {image_id}"); continue
        side = str(row.get("side", "unknown")); box = BBox(image_id, float(row["x_min"]), float(row["y_min"]), float(row["x_max"]), float(row["y_max"]), side, "bbox_csv")
        crop = crop_pil(Image.open(src).convert("RGB"), box, margin=margin); dst = out_dir/f"{image_id}_{side}_periorbital.png"; dst.parent.mkdir(parents=True, exist_ok=True); crop.save(dst)

def crop_from_facemesh(image_dir: Path, out_dir: Path, margin: float):
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
    for p in tqdm([p for p in image_dir.rglob("*") if p.is_file() and p.suffix.lower() in exts]):
        try: boxes = infer_periorbital_boxes_facemesh(p)
        except Exception as e: print(f"Failed {p}: {e}"); continue
        if not boxes: print(f"No face detected: {p}"); continue
        img = Image.open(p).convert("RGB")
        for box in boxes:
            crop = crop_pil(img, box, margin=margin); dst = out_dir/f"{p.stem}_{box.side}_periorbital.png"; dst.parent.mkdir(parents=True, exist_ok=True); crop.save(dst)

def main():
    ap = argparse.ArgumentParser(description="Crop periorbital images locally. No images are included in this repo.")
    ap.add_argument("--image-dir", required=True); ap.add_argument("--out-dir", default="local_outputs/periorbital_crops"); ap.add_argument("--method", choices=["bbox_csv","facemesh"], default="bbox_csv"); ap.add_argument("--bbox-csv"); ap.add_argument("--margin", type=float, default=0.25)
    args = ap.parse_args(); image_dir = Path(args.image_dir); out_dir = Path(args.out_dir)
    if args.method == "bbox_csv":
        if not args.bbox_csv: raise SystemExit("--bbox-csv is required for --method bbox_csv")
        crop_from_bbox_csv(image_dir, Path(args.bbox_csv), out_dir, args.margin)
    else: crop_from_facemesh(image_dir, out_dir, args.margin)
if __name__ == "__main__": main()
