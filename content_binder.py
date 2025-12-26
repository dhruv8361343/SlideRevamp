


def resolve_layout(predictions, features):
    best = predictions[0]
    second = predictions[1]

    # Low confidence
    if best["confidence"] < 0.55:
        return "text_only"

    # Ambiguous
    if abs(best["confidence"] - second["confidence"]) < 0.08:
        return "text_only"

    # Content overrides
    if features["has_table"]:
        return "text_only"

    if features["num_images"] >= 3:
        return "image_grid"

    return best["layout"]



def split_content(slide_meta):
    texts = []
    images = []
    tables = []

    for s in slide_meta["shapes"]:
        if s["has_text"] and s["text"]:
            texts.append(s["text"])
        if s["has_image"]:
            images.append(s["image_path"])
        if s["has_table"]:
            tables.append(s["table_csv"])

    return texts, images, tables

def bind_content(layout, texts, images, tables):
    bound = []

    text_idx = 0
    img_idx = 0

    for el in layout["elements"]:
        if el["type"] == "text" and text_idx < len(texts):
            bound.append({
                **el,
                "content": texts[text_idx]
            })
            text_idx += 1

        elif el["type"] == "image" and img_idx < len(images):
            bound.append({
                **el,
                "source": images[img_idx]
            })
            img_idx += 1

        elif el["type"] == "table" and tables:
            bound.append({
                **el,
                "source": tables[0]
            })

    return bound

def compute_density(text, box):
    """
    box: dict with width & height (normalized 0–1)
    """
    area = box["width"] * box["height"]
    if area == 0:
        return float("inf")
    return len(text) / area

def choose_font_size(density):
    BASE_FONT = 40  # pptx-like title size

    if density < 300:
        return BASE_FONT
    elif density < 600:
        return int(BASE_FONT * 0.85)
    elif density < 900:
        return int(BASE_FONT * 0.7)
    else:
        return int(BASE_FONT * 0.55)

def choose_line_spacing(font_size):
    if font_size >= 36:
        return 1.3
    elif font_size >= 28:
        return 1.2
    else:
        return 1.1

def apply_typography(bound_elements):
    """
    Adds font_size & line_spacing to text elements.
    """
    for el in bound_elements:
        if el["type"] != "text":
            continue

        density = compute_density(el["content"], el)
        font_size = choose_font_size(density)
        line_spacing = choose_line_spacing(font_size)

        el["font_size"] = font_size
        el["line_spacing"] = line_spacing

    return bound_elements

def compute_image_dominance(img_box):
    """
    img_box: dict with width, height (normalized)
    """
    return img_box["width"] * img_box["height"]

def choose_image_scale(dominance):
    if dominance > 0.6:
        return 0.85   # shrink
    elif dominance > 0.3:
        return 0.95   # normal
    else:
        return 1.0    # allow full size

def choose_fit_mode(layout_name):
    if layout_name in ["image_background", "image_grid"]:
        return "cover"
    return "contain"

def apply_image_rules(bound_elements, layout_name):
    for el in bound_elements:
        if el["type"] != "image":
            continue

        dominance = compute_image_dominance(el)
        el["scale"] = choose_image_scale(dominance)
        el["fit"] = choose_fit_mode(layout_name)

        # optional: dim background images
        if layout_name == "image_background":
            el["overlay"] = {
                "color": "black",
                "opacity": 0.35
            }

    return bound_elements
