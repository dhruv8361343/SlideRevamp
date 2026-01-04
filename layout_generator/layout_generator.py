import numpy as np
import pandas as pd
import joblib
import json
from pathlib import Path

LAYOUT_DIR = Path("/kaggle/working/SlideRevamp/layouts")

def build_model_input(features, feature_columns):
    row = {}
    for col in feature_columns:
        if col not in features:
            raise KeyError(f"Missing feature: {col}")
        row[col] = features[col]
    return pd.DataFrame([row])

def predict_layout(features, top_k=2):
    FEATURE_COLUMNS = [
        "num_text_blocks",
        "total_text_length",
        "avg_text_len",
        "num_images",
        "largest_image_area",
        "avg_image_area",
        "img_aspect_ratio",
        "has_table",
        "has_quote",
        "has_digits",
        "is_agenda",
        "slide_density"]
    X = build_model_input(features, FEATURE_COLUMNS)

    layout_model = joblib.load("/kaggle/input/weights-for-layout-generator/layout_generator_xgb (4).pkl")
    label_encoder = joblib.load("/kaggle/input/weights-for-layout-generator/layout_label_encoder (4).pkl")

    probs = layout_model.predict_proba(X)[0]

    top_indices = np.argsort(probs)[-top_k:][::-1]
    layouts = label_encoder.inverse_transform(top_indices)

    return [
        {
            "layout": layouts[i],
            "confidence": float(probs[top_indices[i]])
        }
        for i in range(len(layouts))
    ]

def load_layout_template(layout_name):
    path = LAYOUT_DIR / f"{layout_name}.json"
    if not path.exists():
        raise ValueError(f"Layout template not found: {layout_name}")
    return json.loads(path.read_text())




