# Data Sources and Acquisition Notes

This repository is metadata-only. It does not contain source images, masked images, or cropped images.

Internal source keys are preserved for reproducibility. Use `source_display_name` for papers, posters, README tables, and public documentation.

## Source table

See `data/source_acquisition_manifest.csv` for machine-readable source metadata, permission notes, and access links.

| source_dataset_clean        | source_display_name                              |   n_images_in_dermlatbench | primary_url                                                                                                                  |
|:----------------------------|:-------------------------------------------------|---------------------------:|:-----------------------------------------------------------------------------------------------------------------------------|
| scin_images                 | SCIN: Skin Condition Image Network               |                      10379 | https://github.com/google-research-datasets/scin                                                                             |
| ddidiversedermatologyimages | DDI: Diverse Dermatology Images                  |                        656 | https://aimi.stanford.edu/datasets/ddi-diverse-dermatology-images                                                            |
| skindeep_clinical_images    | Skin Deep: Paediatric Dermatology Image Resource |                        542 | https://dftbskindeep.com/                                                                                                    |
| images_train_mediqa_2025_wv | MEDIQA-WV 2025 train split                       |                        449 | https://sites.google.com/view/mediqa-2025/mediqa-wv                                                                          |
| images_valid_mediqa_2025_wv | MEDIQA-WV 2025 validation split                  |                        147 | https://sites.google.com/view/mediqa-2025/mediqa-wv                                                                          |
| images_test_mediqa_2025_wv  | MEDIQA-WV 2025 test split                        |                        152 | https://sites.google.com/view/mediqa-2025/mediqa-wv                                                                          |
| UMN_Inclusive_Dermatology   | UNM Inclusive Dermatology Atlas                  |                        178 | https://hsc.unm.edu/medicine/departments/dermatology/inclusive-dermatology/                                                  |
| images_mst_e_crop           | MST-E periorbital crop subset                    |                         38 | https://papers.neurips.cc/paper_files/paper/2023/hash/60d25b3210c92f5ba2002a8e1f1adf1c-Abstract-Datasets_and_Benchmarks.html |

## Source-by-source access instructions

### SCIN: Skin Condition Image Network
Review the SCIN Data Use Public License, then download from official SCIN GitHub or Google SCIN Hugging Face. Follow privacy and no re-identification restrictions.

### DDI: Diverse Dermatology Images
Access through the Stanford AIMI Shared Datasets Portal / Redivis workflow. Register for access, accept the DDI Research Use Agreement, and do not share download links or redistribute images.

### Skin Deep: Paediatric Dermatology Image Resource
Contact Skin Deep / Don’t Forget the Bubbles for research use beyond ordinary website viewing. For collections or project permissions, the public submission page directs users to `hello@dontforgetthebubbles.com`.

### MEDIQA-WV 2025 train/validation/test splits
Use the official MEDIQA 2025 / MEDIQA-WV shared-task release page, follow organizer terms, and store images locally.

### UNM Inclusive Dermatology Atlas
Correct display name: `UNM Inclusive Dermatology Atlas`. Internal key retained for backward compatibility: `UMN_Inclusive_Dermatology`. Treat as a source website/educational atlas unless explicit dataset redistribution rights are obtained. Contact UNM Dermatology or the Inclusive Dermatology Atlas project team for permission beyond ordinary viewing.

### MST-E periorbital crop subset
Obtain MST-E source material from the official MST-E / Monk Skin Tone Examples release, follow release terms, and generate periorbital crops locally using `scripts/crop_periorbital_images.py`. Do not redistribute source or cropped images unless explicitly permitted.
