import json
from pathlib import Path
import pandas as pd

def extract_slide_features(slide_dir: Path):
    meta_path = slide_dir / f"{slide_dir.name}_metadata.json"

    with open(meta_path, "r", encoding="utf-8") as f:
        slide = json.load(f)

    shapes = slide["shapes"]

    num_shapes = len(shapes)
    text_shapes = [s for s in shapes if s["has_text"]]
    image_shapes = [s for s in shapes if s["has_image"]]
    table_shapes = [s for s in shapes if s["has_table"]]

    total_text_len = sum(len(s["text"]) for s in text_shapes if s["text"])
    num_text_blocks = len(text_shapes)
    avg_text_len = (
    total_text_len / num_text_blocks
    if num_text_blocks > 0 else 0
    )
    num_images = len(image_shapes)

    img_areas = []
    for img in image_shapes:
        if img["width_norm"] and img["height_norm"]:
            img_areas.append(img["width_norm"] * img["height_norm"])

    largest_img_area = max(img_areas) if img_areas else 0.0
    avg_img_area = sum(img_areas) / len(img_areas) if img_areas else 0.0

    slide_density = round(num_shapes / 10.0, 2)
    return {
    "slide_num": slide["slide_num"],
    "num_shapes": num_shapes,
    "num_text_blocks": num_text_blocks,
    "total_text_length": total_text_len,
    "avg_text_len": round(avg_text_len, 2),   
    "num_images": num_images,
    "largest_image_area": round(largest_img_area, 3),
    "avg_image_area": round(avg_img_area, 3),
    "has_table": int(len(table_shapes) > 0),
    "slide_density": slide_density
}



def build_features_from_ingestion(ingestion_dir):
    rows = []
    ingestion_dir = Path(ingestion_dir)

    for slide_dir in sorted(ingestion_dir.glob("slide_*")):
        rows.append(extract_slide_features(slide_dir))

    return pd.DataFrame(rows)


df_features = build_features_from_ingestion("out(3)")
df_features.head()
df_features.to_csv("real_layou_dataset.csv", index=False)
print(df_features.columns.tolist())
