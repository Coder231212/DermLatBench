from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Optional
from PIL import Image, ImageDraw

MaskPreset = Literal["none", "bottom", "right", "both"]
MaskColor = Literal["neutral_gray", "black", "white"]

@dataclass(frozen=True)
class MaskSpec:
    image_id: str
    filename: str
    manifest_master_filename: str
    mask_preset: MaskPreset = "none"
    right_mask_pct: float = 18.0
    bottom_mask_pct: float = 20.0
    mask_color: MaskColor = "neutral_gray"
    artifact_location: str = ""
    annotation_complete: str = ""

def _normalize_image_id(value: str) -> str:
    return str(value).strip().upper()

def _strip_known_extension(name: str) -> str:
    p = Path(str(name).strip())
    return p.stem.lower() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"} else p.name.lower()

def _coerce_mask_preset(value: Any) -> MaskPreset:
    value = str(value or "").strip().lower()
    return value if value in {"bottom", "right", "both", "none"} else "none"  # type: ignore[return-value]

def _coerce_mask_color(value: Any) -> MaskColor:
    value = str(value or "").strip().lower()
    return value if value in {"neutral_gray", "black", "white"} else "neutral_gray"  # type: ignore[return-value]

def _coerce_float(value: Any, default: float) -> float:
    try:
        return default if value is None or value == "" else float(value)
    except (TypeError, ValueError):
        return default

def _mask_rgb(mask_color: MaskColor) -> tuple[int, int, int]:
    return (0, 0, 0) if mask_color == "black" else (255, 255, 255) if mask_color == "white" else (128, 128, 128)

def load_mask_specs(mask_json_path: str | Path) -> Dict[str, MaskSpec]:
    with Path(mask_json_path).open("r", encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list):
        raise ValueError("Mask annotation JSON must be a list of objects")
    specs: Dict[str, MaskSpec] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        image_id = _normalize_image_id(row.get("image_id", ""))
        if not image_id:
            continue
        specs[image_id] = MaskSpec(
            image_id=image_id,
            filename=str(row.get("filename", "") or ""),
            manifest_master_filename=str(row.get("manifest_master_filename", "") or ""),
            mask_preset=_coerce_mask_preset(row.get("mask_preset", "none")),
            right_mask_pct=_coerce_float(row.get("right_mask_pct"), 18.0),
            bottom_mask_pct=_coerce_float(row.get("bottom_mask_pct"), 20.0),
            mask_color=_coerce_mask_color(row.get("mask_color", "neutral_gray")),
            artifact_location=str(row.get("artifact_location", "") or ""),
            annotation_complete=str(row.get("annotation_complete", "") or ""),
        )
    return specs

def build_filename_index(mask_specs: Dict[str, MaskSpec]) -> Dict[str, str]:
    index: Dict[str, str] = {}
    for image_id, spec in mask_specs.items():
        for c in {image_id.lower(), _strip_known_extension(image_id), Path(spec.filename).name.lower(), _strip_known_extension(spec.filename), Path(spec.manifest_master_filename).name.lower(), _strip_known_extension(spec.manifest_master_filename)}:
            if c:
                index[c] = image_id
    return index

def infer_image_id_from_path(image_path: str | Path, mask_specs: Dict[str, MaskSpec], filename_index: Optional[Dict[str, str]] = None) -> Optional[str]:
    p = Path(image_path)
    filename_index = filename_index or build_filename_index(mask_specs)
    for key in (p.name.lower(), p.stem.lower()):
        if key in filename_index:
            return filename_index[key]
    upper_name = p.name.upper()
    for image_id in mask_specs:
        if image_id in upper_name:
            return image_id
    return None

def apply_mask_to_pil(image: Image.Image, mask_spec: MaskSpec, *, force_rgb: bool = True) -> Image.Image:
    out = image.convert("RGB") if force_rgb else image.copy()
    if mask_spec.mask_preset == "none":
        return out
    width, height = out.size
    draw = ImageDraw.Draw(out)
    fill = _mask_rgb(mask_spec.mask_color)
    right_w = int(round(width * max(0.0, min(float(mask_spec.right_mask_pct), 100.0)) / 100.0))
    bottom_h = int(round(height * max(0.0, min(float(mask_spec.bottom_mask_pct), 100.0)) / 100.0))
    if mask_spec.mask_preset in {"right", "both"} and right_w > 0:
        draw.rectangle((max(0, width - right_w), 0, width, height), fill=fill)
    if mask_spec.mask_preset in {"bottom", "both"} and bottom_h > 0:
        draw.rectangle((0, max(0, height - bottom_h), width, height), fill=fill)
    return out

def open_masked_image(image_path: str | Path, mask_specs: Dict[str, MaskSpec], filename_index: Optional[Dict[str, str]] = None) -> tuple[Image.Image, Optional[MaskSpec]]:
    image = Image.open(image_path)
    image_id = infer_image_id_from_path(image_path, mask_specs, filename_index)
    if image_id is None:
        return image.convert("RGB"), None
    spec = mask_specs[image_id]
    return apply_mask_to_pil(image, spec), spec

def save_masked_local_cache(image_path: str | Path, output_dir: str | Path, mask_specs: Dict[str, MaskSpec], filename_index: Optional[Dict[str, str]] = None, *, overwrite: bool = False, output_format: Literal["PNG", "JPEG"] = "PNG") -> Path:
    output_dir = Path(output_dir); output_dir.mkdir(parents=True, exist_ok=True)
    image_id = infer_image_id_from_path(image_path, mask_specs, filename_index) or Path(image_path).stem
    output_path = output_dir / f"{image_id}_masked{'.png' if output_format == 'PNG' else '.jpg'}"
    if output_path.exists() and not overwrite:
        return output_path
    masked, _ = open_masked_image(image_path, mask_specs, filename_index)
    masked.save(output_path, format=output_format, **({"quality":95,"subsampling":0} if output_format == "JPEG" else {}))
    return output_path

def iter_images(image_dir: str | Path) -> Iterable[Path]:
    for path in Path(image_dir).rglob("*"):
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}:
            yield path
