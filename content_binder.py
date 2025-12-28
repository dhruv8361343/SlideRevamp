


def resolve_layout(predictions, features):
    best = predictions[0]
    second = predictions[1]

    # --- 1. Content Overrides (Highest Priority) ---
    if features["has_table"]:
        return "text_only"

    # If many images, force grid
    if features["num_images"] >= 3:
        return "image_grid"

    # --- 2. Sanity Check for "Text Only" ---
    # If model predicts text_only but we HAVE images, force an image layout
    if best["layout"] == "text_only" and features["num_images"] > 0:
        return "image_right"

    # --- 3. Handle Low Confidence / Ambiguity ---
    is_low_conf = best["confidence"] < 0.55
    is_ambiguous = abs(best["confidence"] - second["confidence"]) < 0.08

    if is_low_conf or is_ambiguous:
        # Fallback logic: Pick a safe layout based on content
        if features["num_images"] > 0:
            return "image_right"  # Safe default if there are images
        else:
            return "text_only"    # Safe default if text only

    return best["layout"]



def split_content(slide_meta):
    texts = []
    images = []
    tables = []

    for s in slide_meta["shapes"]:
        if s["has_text"] and s.get("paragraphs"):
            texts.append(s["paragraphs"])
        if s["has_image"]:
            images.append(s["image_path"])
        if s["has_table"]:
            tables.append(s["table_csv"])

    return texts, images, tables

def bind_content(layout, texts, images, tables):
    bound = []
    text_idx = 0
    img_idx = 0

    # Count text slots so we know when to merge leftover text
    text_slots = [el for el in layout["elements"] if el["type"] == "text"]
    text_slot_count = len(text_slots)
    current_text_slot = 0

    for el in layout["elements"]:
        if el["type"] == "text" and text_idx < len(texts):
            # content is now a LIST of paragraphs
            content = texts[text_idx] 
            current_text_slot += 1
            
            # --- MERGE LOGIC: If this is the last slot, append all remaining text ---
            if current_text_slot == text_slot_count:
                while text_idx + 1 < len(texts):
                    text_idx += 1
                    # Extend the list of paragraphs (rich text merge)
                    content.extend(texts[text_idx])
            
            bound.append({
                **el,
                "content": content # This is now the rich structure
            })
            text_idx += 1

        elif el["type"] == "image" and img_idx < len(images):
            bound.append({ **el, "source": images[img_idx] })
            img_idx += 1

        elif el["type"] == "table" and tables:
            bound.append({ **el, "source": tables[0] })

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
    # Use 'cover' for these layouts to look professional
    if layout_name in ["image_background", "image_grid", "image_left", "image_right"]:
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



