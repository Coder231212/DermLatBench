# DermLatBench

DermLatBench is a metadata-only benchmark for evaluating whether medical vision-language models can map visible anatomy to a stable patient-centered left/right reference frame.

**This repository intentionally contains no actual images.** It contains metadata, labels, source-provenance documentation, permission/access directions, Skin Deep real-time masking code, and local-only periorbital cropping utilities.

Generated: 2026-10-08

## Citation

```text
Liu, A. H., Suzuki, H., Suzuki, S., & Liu, M.H.. (2026). DermLatBench: Repurposing wound and dermatology image databases for AI laterality benchmarking [Conference presentation]. Symposium on Advanced Wound Care (SAWC) Fall, Las Vegas, NV, United States.
```

## LeftRightQuest

A related outreach/demo app is available at:

```text
https://leftrightquest.org
```

LeftRightQuest is intended as a human-facing game/app for exploring anatomical left-right reasoning. It is separate from this metadata-only repository and should not be treated as a source of benchmark image pixels.

## Source dataset names

Internal source keys are preserved for reproducibility. Use `source_display_name` for human-readable reporting.

| source_dataset_clean        | source_display_name                              |   n_images |
|:----------------------------|:-------------------------------------------------|-----------:|
| scin_images                 | SCIN: Skin Condition Image Network               |      10379 |
| ddidiversedermatologyimages | DDI: Diverse Dermatology Images                  |        656 |
| skindeep_clinical_images    | Skin Deep: Paediatric Dermatology Image Resource |        542 |
| images_train_mediqa_2025_wv | MEDIQA-WV 2025 train split                       |        449 |
| UMN_Inclusive_Dermatology   | UNM Inclusive Dermatology Atlas                  |        178 |
| images_test_mediqa_2025_wv  | MEDIQA-WV 2025 test split                        |        152 |
| images_valid_mediqa_2025_wv | MEDIQA-WV 2025 validation split                  |        147 |
| images_mst_e_crop           | MST-E periorbital crop subset                    |         38 |

The main naming correction is:

```text
UMN_Inclusive_Dermatology -> UNM Inclusive Dermatology Atlas
```

The internal key is retained for backward compatibility with existing manifests, but the display name and source documentation have been corrected.

## How to obtain source images

This repository does not download or redistribute images. Users must obtain each source dataset separately and comply with original terms. See:

```text
docs/DATA_SOURCES.md
data/source_acquisition_manifest.csv
```

High-level summary:

- **SCIN**: review/accept the SCIN Data Use Public License; download from official SCIN GitHub or Hugging Face.
- **DDI**: register through Stanford AIMI/Redivis and agree to the DDI Research Use Agreement; do not share download links.
- **Skin Deep**: obtain permission from Skin Deep / Don’t Forget the Bubbles for research use; no raw or masked images are redistributed here.
- **MEDIQA-WV 2025**: obtain official shared-task data from the MEDIQA-WV organizers/release page and follow challenge terms.
- **UNM Inclusive Dermatology Atlas**: treat as an educational atlas/source website unless research permission is documented; contact UNM Dermatology for permission beyond ordinary viewing.
- **MST-E periorbital crop subset**: obtain authorized MST-E source material, then generate crops locally with `scripts/crop_periorbital_images.py`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp configs/source_roots.example.yaml configs/source_roots.yaml
python scripts/summarize_manifest.py
python scripts/verify_no_images.py
```

## Reconstruct local image workspace

```bash
python scripts/build_from_local_sources.py \
  --manifest data/dermlatbench_metadata.csv \
  --source-roots configs/source_roots.yaml \
  --out-dir local_images/dermlatbench \
  --mode symlink
```

Include Skin Deep only if you have authorized local access:

```bash
python scripts/build_from_local_sources.py \
  --allow-skindeep \
  --manifest data/dermlatbench_metadata.csv \
  --source-roots configs/source_roots.yaml \
  --out-dir local_images/dermlatbench \
  --mode symlink
```

## Skin Deep masking

Raw Skin Deep images are not modified. The recommended inference path applies masks in memory from `data/skindeep_mask_annotations_export.json`.

## Periorbital cropping

Use `scripts/crop_periorbital_images.py` with a local authorized source image directory and either a manual bbox CSV or optional FaceMesh.

## Image-use rule

This repo does not store source or derived image pixels. All actual images and derived crops/masks are local-only and ignored by git.
