import numpy as np
import pandas as pd
def build_model_input(features, feature_columns):
    row = {}
    for col in feature_columns:
        if col not in features:
            raise KeyError(f"Missing feature: {col}")
        row[col] = features[col]
    return pd.DataFrame([row])

def predict_layout(features, top_k=2):
    X = build_model_input(features, FEATURE_COLUMNS)

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
