
import math
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
    all_paragraphs = []
    for text_block in texts:
        if isinstance(text_block, list):
            all_paragraphs.extend(text_block)
        else:
            all_paragraphs.append(text_block)
            
    text_slots = [i for i, el in enumerate(layout["elements"]) if el["type"] == "text"]
    num_slots = len(text_slots)
    
    # Create buckets for each text slot
    slot_buckets = [[] for _ in range(num_slots)]
    
    # Distribute paragraphs evenly across all boxes (Round Robin)
    if num_slots > 0:
        for idx, para in enumerate(all_paragraphs):
            slot_buckets[idx % num_slots].append(para)

    img_iter = iter(images)
    table_iter = iter(tables)
    text_count = 0

    for el in layout["elements"]:
        new_el = el.copy()
        if el["type"] == "text":
            new_el["content"] = slot_buckets[text_count]

            if new_el["content"] and isinstance(new_el["content"][0], dict):
                runs = new_el["content"][0].get("runs", [])
                if runs and "color_rgb" in runs[0]:
                    new_el["font_color"] = runs[0]["color_rgb"]
            
            text_count += 1
            bound.append(new_el)
        elif el["type"] == "image":
            try: new_el["source"] = next(img_iter); bound.append(new_el)
            except: pass
        elif el["type"] == "table":
            try: new_el["source"] = next(table_iter); bound.append(new_el)
            except: pass

    return bound
    
def compute_density(text_list, box):
    if not text_list:
        return 0
        
    # CHANGE: Access the text within the new run/level dictionary structure
    total_chars = 0
    for para in text_list:
        if isinstance(para, dict):
            # Sum the length of text in every run
            total_chars += sum(len(run.get("text", "")) for run in para.get("runs", []))
        else:
            total_chars += len(str(para))
    
    area = box.get("width", 0.1) * box.get("height", 0.1)
    if area == 0:
        return float("inf")
        
    return total_chars / area

def choose_font_size(density):
    BASE_FONT = 28 

    # Density thresholds (tuned for 0-1 normalized coordinates)
    # Example: 200 chars in a 0.5x0.5 box (0.25 area) = 800 density
    
    if density < 400:       # Titles only
        return 28
    elif density < 1000:     # Short bullets
        return 24
    elif density < 2000:    # Normal paragraph
        return 18
    elif density < 3500:    # Dense text
        return 14
    else:                   # Wall of text
        return 10           # Go smaller to ensure fit

def choose_line_spacing(font_size):
    # Smaller fonts need slightly more breathing room proportionally, 
    if font_size >= 24:
        return 1.2
    elif font_size >= 18:
        return 1.15
    else:
        return 1.1

def apply_typography(bound_elements):
    """
    Adds font_size & line_spacing to text elements.
    """
    for el in bound_elements:
        if el["type"] != "text":
            continue

        # Check if content exists to avoid errors
        content = el.get("content", [])
        
        density = compute_density(content, el)
        font_size = choose_font_size(density)
        line_spacing = choose_line_spacing(font_size)

        el["font_size"] = font_size
        el["line_spacing"] = line_spacing

    return bound_elements

def compute_image_dominance(img_box):
    """
    img_box: dict with width, height (normalized)
    """
    return img_box.get("width", 0) * img_box.get("height", 0)

def choose_image_scale(dominance, layout_name):
    # CRITICAL FIX: Never shrink a background image!
    if layout_name == "image_background":
        return 1.0

    # For other layouts, adding whitespace (padding) can look nice
    if dominance > 0.6:
        return 0.90   # Slight padding for very large images
    elif dominance > 0.3:
        return 0.95   # Minimal padding
    else:
        return 1.0    # Small images can stay full size

def choose_fit_mode(layout_name):
    # UPDATED: Added 'image_top' and 'image_bottom'
    # "cover" ensures the image fills the shape completely (cropping edges if needed)
    # This looks much better for splitting slides (left/right/top/bottom)
    cover_layouts = [
        "image_background", 
        "image_grid", 
        "image_left", 
        "image_right", 
        "image_top", 
        "image_bottom"
    ]
    
    if layout_name in cover_layouts:
        return "cover"
        
    # "contain" ensures the whole image is visible (good for charts/diagrams in text slides)
    return "contain"

def apply_image_rules(bound_elements, layout_name):
    for el in bound_elements:
        if el["type"] != "image":
            continue

        dominance = compute_image_dominance(el)
        
        # Pass layout_name to protect background images
        el["scale"] = choose_image_scale(dominance, layout_name)
        el["fit"] = choose_fit_mode(layout_name)

        # Standard Dimming for Backgrounds (Text readability)
        if layout_name == "image_background":
            el["overlay"] = {
                "color": "black",
                "opacity": 0.40  # Slightly darker for better contrast
            }

    return bound_elements










