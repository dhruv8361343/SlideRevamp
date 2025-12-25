import json
from pathlib import Path
import numpy as np

def compute_slide_features(slide_meta_path: Path):
    slide = json.loads(slide_meta_path.read_text())

    text_blocks = 0
    total_text_len = 0
    image_areas = []
    has_table = 0

    for s in slide["shapes"]:
        # text
        if s.get("has_text"):
            text_blocks += 1
            if s.get("text"):
                total_text_len += len(s["text"])

        # image
        if s.get("has_image"):
            w = s.get("width_norm", 0) or 0
            h = s.get("height_norm", 0) or 0
            image_areas.append(w * h)

        # table
        if s.get("has_table"):
            has_table = 1

     features = {
         "num_shapes": len(slide["shapes"]),
         "num_text_blocks": text_blocks,
         "total_text_length": total_text_len,
         "avg_text_len": (total_text_len / text_blocks) if text_blocks > 0 else 0,
         "num_images": len(image_areas),
         "largest_image_area": max(image_areas) if image_areas else 0.0,
         "avg_image_area": float(np.mean(image_areas)) if image_areas else 0.0,
         "has_table": has_table,
         "slide_density": len(slide["shapes"]) / 10.0  # normalized proxy
    }

    return features

def collect_all_slides_features(ppt_output_dir: Path):
    slide_features = []

    for slide_dir in sorted(ppt_output_dir.glob("slide_*")):
        meta_path = slide_dir / f"{slide_dir.name}_metadata.json"
        if meta_path.exists():
            features = compute_slide_features(meta_path)
            slide_features.append(features)

    return slide_features



