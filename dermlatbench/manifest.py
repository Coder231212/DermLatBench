from __future__ import annotations
from pathlib import Path
from typing import Dict, Optional
import pandas as pd
import yaml
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}

def load_manifest(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    for col in ["image_id", "source_dataset_clean"]:
        if col not in df.columns:
            raise ValueError(f"Manifest lacks {col}: {path}")
    return df

def load_source_roots(path: str | Path) -> Dict[str, Path]:
    with Path(path).open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    roots = cfg.get("source_roots", cfg)
    return {str(k): Path(v).expanduser() for k, v in roots.items()}

def strip_ext(name: str) -> str:
    p = Path(str(name))
    return p.stem.lower() if p.suffix.lower() in IMAGE_EXTS else p.name.lower()

def index_images(root: Path) -> Dict[str, Path]:
    index: Dict[str, Path] = {}
    if not root.exists():
        return index
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            for key in {p.name.lower(), strip_ext(p.name)}:
                index.setdefault(key, p)
    return index

def resolve_row_image(row: pd.Series, source_roots: Dict[str, Path], indexes: Optional[Dict[str, Dict[str, Path]]] = None) -> Optional[Path]:
    source = str(row.get("source_dataset_clean", ""))
    root = source_roots.get(source)
    if root is None:
        return None
    indexes = indexes or {}
    if source not in indexes:
        indexes[source] = index_images(root)
    idx = indexes[source]
    candidates = [row.get("filename", ""), row.get("manifest_master_filename", ""), f"{row.get('image_id', '')}.jpg", f"{row.get('image_id', '')}.jpeg", f"{row.get('image_id', '')}.png"]
    for cand in candidates:
        if not cand:
            continue
        name = Path(str(cand)).name.lower()
        for key in (name, strip_ext(name)):
            if key in idx:
                return idx[key]
    return None
