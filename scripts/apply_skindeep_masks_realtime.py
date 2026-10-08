#!/usr/bin/env python3
import argparse
from dermlatbench.masking import build_filename_index, iter_images, load_mask_specs, save_masked_local_cache

def main():
    ap = argparse.ArgumentParser(description="Apply SkinDeep masks to a private local cache. Do not distribute generated images.")
    ap.add_argument("--mask-json", default="data/skindeep_mask_annotations_export.json"); ap.add_argument("--image-dir", required=True); ap.add_argument("--out-dir", default="masked_cache/skindeep"); ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args(); specs = load_mask_specs(args.mask_json); index = build_filename_index(specs); n=0
    for image_path in iter_images(args.image_dir):
        out = save_masked_local_cache(image_path, args.out_dir, specs, index, overwrite=args.overwrite, output_format="PNG")
        print(f"{image_path} -> {out}"); n += 1
    print(f"Processed {n} local images")
if __name__ == "__main__": main()
