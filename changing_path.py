from pathlib import Path
import json

def resolve_image_path(raw_image_path, base_dir):
    """
    Converts raw image path to enhanced image path if available.

    raw_image_path: e.g. "images/slide01_shape2_img.png"
    base_dir: Path to ingestion output root
    """

    raw_path = base_dir / raw_image_path

    # Construct enhanced image path
    enhanced_name = raw_path.stem  + raw_path.suffix
    enhanced_path = base_dir / "images_final" / enhanced_name

    # Prefer enhanced if exists
    if enhanced_path.exists():
        return str(enhanced_path.relative_to(base_dir))

    # Fallback to raw
    return raw_image_path
  
def update_slide_metadata_images(slide_json_path, base_dir):
    slide_json_path = Path(slide_json_path)

    data = json.loads(slide_json_path.read_text())

    for shape in data["shapes"]:
        if shape.get("has_image") and shape.get("image_path"):
            shape["image_path"] = resolve_image_path(
                shape["image_path"],
                base_dir
            )

    slide_json_path.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

def update_all_slides(base_dir):
    base_dir = Path(base_dir)

    for slide_dir in base_dir.glob("slide_*"):
        for slide_json in slide_dir.glob("*_metadata.json"):
            update_slide_metadata_images(slide_json, base_dir)

    print("✅ All slide metadata updated with enhanced image paths."
  

