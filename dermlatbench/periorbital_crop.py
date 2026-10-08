from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from PIL import Image

@dataclass(frozen=True)
class BBox:
    image_id: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    side: str = "unknown"
    source: str = "manual"

def clamp_bbox(box: BBox, width: int, height: int) -> BBox:
    return BBox(box.image_id, max(0, min(width, box.x_min)), max(0, min(height, box.y_min)), max(0, min(width, box.x_max)), max(0, min(height, box.y_max)), box.side, box.source)

def expand_bbox(box: BBox, width: int, height: int, margin: float = 0.25) -> BBox:
    w, h = box.x_max - box.x_min, box.y_max - box.y_min
    return clamp_bbox(BBox(box.image_id, box.x_min - w*margin, box.y_min - h*margin, box.x_max + w*margin, box.y_max + h*margin, box.side, box.source), width, height)

def crop_pil(image: Image.Image, box: BBox, *, margin: float = 0.25) -> Image.Image:
    width, height = image.size
    b = expand_bbox(box, width, height, margin=margin)
    return image.crop((round(b.x_min), round(b.y_min), round(b.x_max), round(b.y_max)))

def infer_periorbital_boxes_facemesh(image_path: str | Path) -> list[BBox]:
    try:
        import cv2
        import mediapipe as mp
    except ImportError as e:
        raise ImportError("Install optional dependencies: pip install mediapipe opencv-python") from e
    image_path = Path(image_path)
    img_bgr = cv2.imread(str(image_path))
    if img_bgr is None:
        raise ValueError(f"Could not read image: {image_path}")
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    h, w = img_rgb.shape[:2]
    face_mesh = mp.solutions.face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True)
    result = face_mesh.process(img_rgb); face_mesh.close()
    if not result.multi_face_landmarks:
        return []
    landmarks = result.multi_face_landmarks[0].landmark
    right_eye_idx = [33,246,161,160,159,158,157,173,133,155,154,153,145,144,163,7,70,63,105,66,107]
    left_eye_idx = [263,466,388,387,386,385,384,398,362,382,381,380,374,373,390,249,336,296,334,293,300]
    def mk(indices: list[int], side: str) -> BBox:
        xs = [landmarks[i].x*w for i in indices]; ys = [landmarks[i].y*h for i in indices]
        return BBox(image_path.stem, min(xs), min(ys), max(xs), max(ys), side, "mediapipe_facemesh")
    return [mk(left_eye_idx, "left_eye"), mk(right_eye_idx, "right_eye")]
