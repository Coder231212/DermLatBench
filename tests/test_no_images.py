from pathlib import Path
IMAGE_EXTS={".jpg",".jpeg",".png",".webp",".bmp",".tif",".tiff"}
def test_no_images_in_repo_directories():
    root=Path(__file__).resolve().parents[1]; allow={"local_images","local_outputs","masked_cache",".git"}; bad=[]
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
            rel=p.relative_to(root)
            if not (rel.parts and rel.parts[0] in allow): bad.append(str(rel))
    assert not bad, f"Image files found in repo directories: {bad}"
