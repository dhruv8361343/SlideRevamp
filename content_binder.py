
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
    """
    Binds content to the layout slots. 
    Smart Feature: Distributes text paragraphs evenly across available text slots.
    """
    bound = []
    
    #  Flatten all text into a single list of paragraphs 
    # This allows us to reflow text from 1 box into 2 or 3 columns
    all_paragraphs = []
    for text_block in texts:
        if isinstance(text_block, list):
            all_paragraphs.extend(text_block)
        else:
            all_paragraphs.append(text_block)

    # Prepare Iterators 
    img_iter = iter(images)
    table_iter = iter(tables)
    
    #  Calculate Text Distribution  
    text_slots = [el for el in layout["elements"] if el["type"] == "text"]
    num_text_slots = len(text_slots)
    
    
    if num_text_slots > 0 and all_paragraphs:
        avg_paras = len(all_paragraphs) / num_text_slots
        chunk_size = math.ceil(avg_paras)
    else:
        chunk_size = 0

    current_para_idx = 0

    #  Bind Elements 
    for el in layout["elements"]:
        
        # text logic (Smart Reflow) 
        if el["type"] == "text":
            # Determine range of paragraphs for this specific slot
            start = current_para_idx
            end = start + chunk_size
            
            # If this is the LAST text slot, take everything remaining
            is_last_text_slot = (bound.count(el) == num_text_slots - 1) # Rough check
            # A safer check is counting how many text slots we've processed:
            slots_processed = len([b for b in bound if b["type"] == "text"])
            
            if slots_processed == num_text_slots - 1:
                end = len(all_paragraphs)
            
            # Slice the paragraphs for this slot
            slot_content = all_paragraphs[start:end]
            
            # Update index for next loop
            current_para_idx = end
            
            bound.append({
                **el,
                "content": slot_content
            })

        # --- IMAGE LOGIC ---
        elif el["type"] == "image":
            try:
                img_source = next(img_iter)
                bound.append({**el, "source": img_source})
            except StopIteration:
                # If we run out of images, we skip this slot (or you could put a placeholder)
                pass

        # --- TABLE LOGIC ---
        elif el["type"] == "table":
            try:
                table_source = next(table_iter)
                bound.append({**el, "source": table_source})
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
    
    if density < 500:       # Very sparse text
        return 28
    elif density < 1000:    # Normal bullet points
        return 24
    elif density < 1500:    # Dense paragraph
        return 18
    elif density < 2500:    # Very dense
        return 14
    else:                   # "Wall of text" - preventative measure
        return 11

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


