# Image Use Policy

This repository is designed to respect source-image use restrictions.

Users must obtain each source image collection separately and comply with the original terms. See `docs/DATA_SOURCES.md` and `data/source_acquisition_manifest.csv`.

Do not commit raw source images, masked images, or cropped periorbital images. Keep all local image material under `local_images/`, `local_outputs/`, or `masked_cache/`.

Skin Deep masks are applied in memory at inference time using `data/skindeep_mask_annotations_export.json`.

Periorbital crops are derived images and should be generated only locally from authorized source images.

Run:

```bash
python scripts/verify_no_images.py
```
