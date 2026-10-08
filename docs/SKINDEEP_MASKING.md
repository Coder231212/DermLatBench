# SkinDeep Masking

`data/skindeep_mask_annotations_export.json` stores mask instructions, not pixels. Use `dermlatbench.masking.open_masked_image()` during inference. Private local caches can be created with `scripts/apply_skindeep_masks_realtime.py`; do not distribute generated masked images.
