# SkinDeep GT reconciliation (2026-11-20)

20 revised laterality labels from the completed SkinDeep annotation review were synchronized into both SkinDeep and full DermLatBench ground-truth files. See the CSV in this folder for a row-level audit. Original human votes and consensus fields are unchanged.

Two newer explicit manual corrections take precedence and remain unchanged:
- DLB_00012001: LEFT (older export: RIGHT)
- DLB_00012096: RIGHT (older export: UNABLE_TO_DETERMINE)

Updated source label: `SKINDEEP_MASK_ANNOTATION_REVIEW_20261008`. These reviewer annotations must not be mistaken for independent three-rater consensus. Recompute manuscript model metrics after this GT revision. No source, masked, or cropped images are included.
