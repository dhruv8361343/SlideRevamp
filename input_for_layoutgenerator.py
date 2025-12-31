import json
from pathlib import Path
import pandas as pd
import re

def extract_slide_features(slide_dir: Path):
  
    meta_path = slide_dir / f"{slide_dir.name}_metadata.json"
    
    
    if not meta_path.exists():
        return {k: 0 for k in [
            "num_text_blocks", "total_text_length", "avg_text_len", "num_images",
            "largest_image_area", "avg_image_area", "img_aspect_ratio",
            "has_table", "has_quote", "has_digits", "is_agenda", "slide_density"
        ]}

    with open(meta_path, "r", encoding="utf-8") as f:
        slide = json.load(f)

    shapes = slide.get("shapes", [])
    
    # 2. Extract Shape Collections
    text_shapes = [s for s in shapes if s.get("has_text") and s.get("text")]
    image_shapes = [s for s in shapes if s.get("has_image")]
    table_shapes = [s for s in shapes if s.get("has_table")]

    # 3. Calculate Text Features
    num_text_blocks = len(text_shapes)
    
    # Combine all text into one string for easier analysis
    all_text_content = " ".join([s["text"] for s in text_shapes])
    total_text_length = len(all_text_content)
    
    if num_text_blocks > 0:
        avg_text_len = total_text_length / num_text_blocks
    else:
        avg_text_len = 0.0

    # 4. Calculate Image Features
    num_images = len(image_shapes)
    img_areas = []
    aspect_ratios = []

    for img in image_shapes:
        w = img.get("width_norm", 0)
        h = img.get("height_norm", 0)
        
        # Area calculation
        if w and h:
            img_areas.append(w * h)
            
        # Aspect Ratio (Width / Height)
        if h > 0:
            aspect_ratios.append(w / h)
        else:
            aspect_ratios.append(0.0)

    # Defaults if no images exist
    largest_image_area = max(img_areas) if img_areas else 0.0
    avg_image_area = sum(img_areas) / len(img_areas) if img_areas else 0.0
    img_aspect_ratio = sum(aspect_ratios) / len(aspect_ratios) if aspect_ratios else 0.0

    # 5. Calculate Boolean/Content Features
    has_table = 1 if len(table_shapes) > 0 else 0
    
    # Check for quotes (standard " or smart quotes “ ”)
    has_quote = 1 if any(char in all_text_content for char in ['"', '“', '”']) else 0
    
    # Check for any digits (0-9) in the text
    has_digits = 1 if any(char.isdigit() for char in all_text_content) else 0
    
    # Check for "Agenda" keywords (case-insensitive)
    agenda_keywords = ["agenda", "table of contents", "overview", "index", "contents"]
    lower_text = all_text_content.lower()
    is_agenda = 1 if any(kw in lower_text for kw in agenda_keywords) else 0

    # 6. Calculate Density
    # Heuristic: Total shapes divided by 10 (arbitrary normalization)
    slide_density = round(len(shapes) / 10.0, 2)

    # 7. Return Dictionary (Strict Order)
    return {
        "num_text_blocks": num_text_blocks,
        "total_text_length": total_text_length,
        "avg_text_len": round(avg_text_len, 2),
        "num_images": num_images,
        "largest_image_area": round(largest_image_area, 3),
        "avg_image_area": round(avg_image_area, 3),
        "img_aspect_ratio": round(img_aspect_ratio, 3),
        "has_table": has_table,
        "has_quote": has_quote,
        "has_digits": has_digits,
        "is_agenda": is_agenda,
        "slide_density": slide_density
    }
    



def build_features_from_ingestion(ingestion_dir):
    rows = []
    ingestion_dir = Path(ingestion_dir)

    for slide_dir in sorted(ingestion_dir.glob("slide_*")):
        rows.append(extract_slide_features(slide_dir))

    return pd.DataFrame(rows)



