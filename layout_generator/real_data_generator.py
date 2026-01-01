import os
import json
import pandas as pd
from pathlib import Path
import numpy as np
import re

INGESTION_DIR = Path("out(1)")   # input directory
OUTPUT_CSV = "real_layout_dataset.csv"

# LAYOUT LABELS (16 Classes)
LAYOUT_CLASSES = {
    0: "text_only",
    1: "title_center",
    2: "two_column",
    3: "three_column",
    4: "four_column",
    5: "image_left",
    6: "image_right",
    7: "image_top",
    8: "image_bottom",
    9: "image_grid",
    10: "image_background",
    11: "big_stat",
    12: "quote",
    13: "timeline",
    14: "table_center",
    15: "agenda"
}

# Reverse map for easier coding(key becomes value and value becomes key in dictionary)
LABEL_TO_ID = {v: k for k, v in LAYOUT_CLASSES.items()}

#  (The 16-Class Logic)
def teacher_layout_rule(row):
    # Unpack features
    imgs = row["num_images"]
    txt_blocks = row["num_text_blocks"]
    txt_len = row["total_text_length"]
    table = row["has_table"]
    
    # New features
    ratio = row["img_aspect_ratio"]
    quote = row["has_quote"]
    digits = row["has_digits"]
    agenda = row["is_agenda"]

    
    if table:
        return "table_center"
    if agenda:
        return "agenda"

  
    if imgs <= 1 and quote:
        return "quote"
    
    if imgs == 0 and digits and txt_len < 100:
        return "big_stat"

    if imgs == 0:
        if txt_len < 300:
            return "title_center"
        
        if txt_blocks == 2:
            return "two_column"
        elif txt_blocks == 3:
            return "three_column"
        elif txt_blocks == 4:
            return "four_column" 
        elif txt_blocks >= 5:
            return "timeline"
            
        return "text_only"

  
    if imgs == 1:
        # Background check (Large image + low text)
        if row["largest_image_area"] > 0.8 and txt_len < 200:
            return "image_background"
            
        # Wide images (> 1.5 ratio) -> Top or Bottom
        if ratio > 1.5:
            # Simple heuristic: if text is short, maybe bottom? Default to top.
            return "image_top" 
        # Tall/Square images -> Left or Right
        else:
            return "image_right" # Default to right for consistency

   
    if imgs >= 2:
        return "image_grid"

    return "text_only" # Fallback


rows = []

print(f"Processing real slides from: {INGESTION_DIR}")

# Check if folder exists
if not INGESTION_DIR.exists():
    print(f"Error: Directory {INGESTION_DIR} not found.")
    exit()

for slide_dir in sorted(INGESTION_DIR.iterdir()):
    if not slide_dir.is_dir() or not slide_dir.name.startswith("slide_"):
        continue

    # Find first matching json/csv
    try:
        meta_file = next(slide_dir.glob("*_metadata.json")) 
    except StopIteration:
        continue # Skip if missing files

    with open(meta_file, "r", encoding="utf-8") as f:
        slide = json.load(f)

    shapes = slide["shapes"]

    # text features
    text_shapes = [s for s in shapes if s.get("has_text") and s.get("text")]
    num_text_blocks = len(text_shapes)

    # Combine all text to check for keywords
    all_text_combined = " ".join([s.get("text", "") for s in text_shapes])
    total_text_len = len(all_text_combined)

    avg_text_len = (
        total_text_len / num_text_blocks
        if num_text_blocks > 0 else 0
    )

    # image features
    image_shapes = [s for s in shapes if s.get("has_image")]
    num_images = len(image_shapes)

    largest_img_area = 0.0
    avg_img_area = 0.0
    img_aspect_ratio = 0.0

    if num_images > 0:
        # Calculate areas and ratios from normalized coords
        areas = []
        ratios = []
        for img in image_shapes:
            w = img.get("width_norm", 0)
            h = img.get("height_norm", 0)
            areas.append(w * h)
            if h > 0:
                ratios.append(w / h)
        
        largest_img_area = max(areas) if areas else 0
        avg_img_area = sum(areas) / len(areas) if areas else 0
        
        # I use the aspect ratio of the LARGEST image to decide layout
        #  the hero image dictates the layout)
        if areas:
            max_idx = areas.index(largest_img_area)
            img_aspect_ratio = ratios[max_idx]
            
    
    has_table = int(any(s.get("has_table") for s in shapes))
    
    has_digits = 1 if re.search(r'[\d%$]', all_text_combined) else 0
    

    has_quote = 1 if re.search(r'["“”]', all_text_combined) else 0
    
    # Check first few words or title for "Agenda", "Contents"
    is_agenda = 0
    if len(all_text_combined) > 0:
        # Check the first text block (likely title)
        title_cand = text_shapes[0].get("text", "").lower()
        if any(x in title_cand for x in ["agenda", "contents", "overview", "summary", "roadmap"]):
            is_agenda = 1

    # structural features
    num_shapes = len(shapes)
    slide_density = round(num_shapes / 10.0, 3)

    # final row
    row = {
        "num_shapes": num_shapes,
        "num_text_blocks": num_text_blocks,
        "total_text_length": total_text_len,
        "avg_text_len": round(avg_text_len, 2),
        "num_images": num_images,
        "largest_image_area": round(largest_img_area, 4),
        "avg_image_area": round(avg_img_area, 4),
        "img_aspect_ratio": round(img_aspect_ratio, 2),
        "has_table": has_table,
        "has_quote": has_quote,
        "has_digits": has_digits,
        "is_agenda": is_agenda,
        "slide_density": slide_density,
        
    }

    # label
    row["layout_class_name"] = teacher_layout_rule(row)
    # Map back to ID 
    row["layout_class"] = LABEL_TO_ID.get(row["layout_class_name"], 0)
    row["source"] = "real"

    rows.append(row)

#save
if not rows:
    print("No slides found! Check INGESTION_DIR path.")
else:
    file_exists = os.path.exists(OUTPUT_CSV)
    df = pd.DataFrame(rows)
    
    # Save
    df.to_csv(OUTPUT_CSV, 
              mode="a",              # append mode
              header=not file_exists, # write header only once
              index=False)

    print(f"Real layout dataset created: {OUTPUT_CSV}")
    print(f"Rows processed: {len(df)}")
    print("\nClass Distribution Found in Real Data:")
    print(df["layout_class_name"].value_counts())