#!/usr/bin/env python3
import argparse
from pathlib import Path
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
def main():
    ap = argparse.ArgumentParser(description="Fail if image files are present in repo-tracked directories."); ap.add_argument("--root", default="."); args = ap.parse_args(); root = Path(args.root); allow = {"local_images","local_outputs","masked_cache",".git"}; bad=[]
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            rel = p.relative_to(root)
            if not (rel.parts and rel.parts[0] in allow): bad.append(str(rel))
    if bad:
        print("Image files found in non-local repo directories:"); [print(f"  {b}") for b in bad]; raise SystemExit(1)
    print("OK: no image files found outside local-only directories.")
if __name__ == "__main__": main()
