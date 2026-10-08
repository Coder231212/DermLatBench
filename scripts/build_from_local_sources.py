#!/usr/bin/env python3
import argparse, os, shutil
from pathlib import Path
from tqdm import tqdm
from dermlatbench.manifest import load_manifest, load_source_roots, resolve_row_image

def link_or_copy(src: Path, dst: Path, mode: str):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink(): return
    os.symlink(src.resolve(), dst) if mode == "symlink" else shutil.copy2(src, dst)

def main():
    ap = argparse.ArgumentParser(description="Create a local image workspace from authorized source datasets. Does not download images.")
    ap.add_argument("--manifest", default="data/dermlatbench_metadata.csv"); ap.add_argument("--source-roots", default="configs/source_roots.yaml")
    ap.add_argument("--out-dir", default="local_images/dermlatbench"); ap.add_argument("--mode", choices=["symlink","copy"], default="symlink")
    ap.add_argument("--allow-skindeep", action="store_true")
    args = ap.parse_args(); manifest = load_manifest(args.manifest); roots = load_source_roots(args.source_roots); out_dir = Path(args.out_dir); indexes = {}; missing=[]; written=0
    for _, row in tqdm(manifest.iterrows(), total=len(manifest)):
        source = str(row["source_dataset_clean"])
        if source == "skindeep_clinical_images" and not args.allow_skindeep: continue
        src = resolve_row_image(row, roots, indexes)
        if src is None:
            missing.append({"image_id": row.get("image_id"), "source_dataset_clean": source, "filename": row.get("filename")}); continue
        link_or_copy(src, out_dir/source/f"{row['image_id']}{src.suffix.lower()}", args.mode); written += 1
    if missing:
        import pandas as pd; pd.DataFrame(missing).to_csv(out_dir/"missing_images.csv", index=False)
    print(f"Wrote/local-linked {written} files under {out_dir}; missing {len(missing)}")
if __name__ == "__main__": main()
