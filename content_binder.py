
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
    
    # 1. Flatten all text into a single list of paragraphs
    all_paragraphs = []
    for text_block in texts:
        if isinstance(text_block, list):
            all_paragraphs.extend(text_block)
        else:
            all_paragraphs.append(text_block)

    # 2. Identify Text Slots & Pre-calculate Distribution (Round Robin)
    text_layout_indices = [i for i, el in enumerate(layout["elements"]) if el["type"] == "text"]
    num_text_slots = len(text_layout_indices)
    
    # Create buckets for each slot
    slot_allocations = [[] for _ in range(num_text_slots)]
    
    # Distribute paragraphs evenly (Card dealing style)
    if num_text_slots > 0:
        for i, para in enumerate(all_paragraphs):
            target_bucket = i % num_text_slots
            slot_allocations[target_bucket].append(para)

    # Prepare Iterators for Images/Tables
    img_iter = iter(images)
    table_iter = iter(tables)
    
    # Track which text bucket we are currently processing
    text_bucket_idx = 0

    # 3. Bind Elements
    for i, el in enumerate(layout["elements"]):
        new_el = el.copy() # Create a copy to avoid modifying template
        
        if el["type"] == "text":
            # Grab the pre-assigned bucket of paragraphs
            if text_bucket_idx < len(slot_allocations):
                new_el["content"] = slot_allocations[text_bucket_idx]
                text_bucket_idx += 1
            else:
                new_el["content"] = []
            bound.append(new_el)

        elif el["type"] == "image":
            try:
                new_el["source"] = next(img_iter)
                bound.append(new_el)
            except StopIteration:
                pass # Skip if no images left

        elif el["type"] == "table":
            try:
                new_el["source"] = next(table_iter)
                bound.append(new_el)
            except StopIteration:
                pass

    return bound
def compute_density(text_list, box):
    """
    Calculates characters per unit of area.
    text_list: List of strings (paragraphs)
    box: dict with width & height (normalized 0-1)
    """
    if not text_list:
        return 0
        
    # Joining the list to count actual characters, not just number of paragraphs
    total_chars = sum(len(p) for p in text_list)
    
    # Avoid division by zero
    area = box.get("width", 0.1) * box.get("height", 0.1)
    if area == 0:
        return float("inf")
        
    return total_chars / area

def choose_font_size(density):
    BASE_FONT = 28 

    # Density thresholds (tuned for 0-1 normalized coordinates)
    # Example: 200 chars in a 0.5x0.5 box (0.25 area) = 800 density
    
    if density < 200:       # Titles only
        return 28
    elif density < 600:     # Short bullets
        return 24
    elif density < 1200:    # Normal paragraph
        return 18
    elif density < 2500:    # Dense text
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





