from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import csv
from PIL import Image
import os
from pathlib import Path
from pptx.enum.text import MSO_AUTO_SIZE,PP_ALIGN

prs = Presentation()


ASSETS_DIR = Path("/kaggle/working/outputs")


def apply_background(slide, bg_path):
    slide.shapes.add_picture(
        str(bg_path),
        left=Inches(0),
        top=Inches(0),
        width=prs.slide_width,
        height=prs.slide_height
    )
def n2pt(x, y, w, h):
    return (
        int(x * prs.slide_width),
        int(y * prs.slide_height),
        int(w * prs.slide_width),
        int(h * prs.slide_height)
    )
def safe_apply_color(font, color_data):
    """Robustly applies color from various formats (hex, tuple, name)."""
    if not color_data:
        return

    # Clean string
    c_str = str(color_data).lower().replace("#", "").replace(" ", "").replace("(", "").replace(")", "")
    
    # Handle known names manually if needed
    if "green" in c_str: 
        font.color.rgb = RGBColor(0, 128, 0)
        return
        
    # Handle Hex (6 chars)
    if len(c_str) == 6:
        try:
            font.color.rgb = RGBColor.from_string(c_str)
        except: pass
    
    # Handle Tuple string '0,255,0'
    elif "," in c_str:
        try:
            parts = c_str.split(",")
            if len(parts) >= 3:
                font.color.rgb = RGBColor(int(parts[0]), int(parts[1]), int(parts[2]))
        except: pass

def parse_color(color_val):
    """Handles Hex, Tuples, and common named colors."""
    if not color_val: return None
    c = str(color_val).lower().strip().replace("#", "")
    
    # Handle common names
    named_colors = {"green": "008000", "red": "FF0000", "blue": "0000FF", "white": "FFFFFF", "black": "000000"}
    if c in named_colors: return RGBColor.from_string(named_colors[c])
    
    # Handle Hex
    if len(c) == 6:
        try: return RGBColor.from_string(c)
        except: pass
        
    # Handle Tuple strings like "(0, 128, 0)"
    if "," in c:
        try:
            rgb = [int(x.strip()) for x in c.replace("(", "").replace(")", "").split(",")]
            return RGBColor(rgb[0], rgb[1], rgb[2])
        except: pass
    return None

# Inside add_text run loop, replace the color block with:
            hex_color = run_data.get("color_rgb") or run_data.get("font_color")
            parsed = parse_color(hex_color)
            if parsed:
                font.color.rgb = parsed
                
def add_text(slide, el):
    l, t, w, h = n2pt(el["x"], el["y"], el["width"], el["height"])
    
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    # CRITICAL FIX: Auto-size must be set on the text_frame
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE 
    
    # Alignment Mapping
    align_map = {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
        "justify": PP_ALIGN.JUSTIFY
    }
    layout_align = el.get("style", {}).get("align", "left")
    align_enum = align_map.get(layout_align, PP_ALIGN.LEFT)

    content_data = el.get("content", [])

    if isinstance(content_data, str):
        p = tf.paragraphs[0]
        p.text = content_data
        p.alignment = align_enum
        return

    for i, para_data in enumerate(content_data):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align_enum
        
        # Check if para_data is a list of runs or a simple dict/string
        # (Binder flattening might leave mixed types, safe check:)
        if not isinstance(para_data, list):
             # Try to extract text if it's a dict, else stringify
             p.text = para_data.get("text", "") if isinstance(para_data, dict) else str(para_data)
             continue

        for run_data in para_data:
            run = p.add_run()
            run.text = run_data.get("text", "")
            
            font = run.font
            # Flexible Key Checks
            if run_data.get("bold") or run_data.get("font_bold"): font.bold = True
            if run_data.get("italic") or run_data.get("font_italic"): font.italic = True
            
            # COLOR FIX: Use the robust helper
            raw_color = run_data.get("color_rgb") or run_data.get("font_color")
            safe_apply_color(font, raw_color)
            
            # SIZE FIX:
            # Do NOT set font.size here if you want Auto-Fit to work perfectly.
            # However, if you must set a MAX size, set it larger than needed.
            # Ideally, rely on the "style" -> "font_size" from layout only.
            
            # Only apply explicit size if it's notably different/header
            # Otherwise let Auto-Fit handle the shrinking.
            layout_size = el.get("font_size", 18)
            if layout_size > 24: # Only enforce size for Titles/Headers
                 font.size = Pt(layout_size)
                    




def add_image(slide, el):
    l, t, w, h = n2pt(el["x"], el["y"], el["width"], el["height"])
    
    # Construct full path
    image_path = ASSETS_DIR / el["source"]
    
    if not image_path.exists():
        print(f"Image missing: {image_path}")
        return

    # 1. Load to get dimensions
    with Image.open(image_path) as img:
        img_w, img_h = img.size

    frame_ratio = w / h
    img_ratio = img_w / img_h
    
    # 2. Add Picture
    pic = slide.shapes.add_picture(str(image_path), l, t)
    
    # 3. Check Fit Mode (Calculated in previous step)
    fit_mode = el.get("fit", "contain") # Default to contain for safety

    if fit_mode == "cover":
        # --- CROP TO FILL ---
        if frame_ratio > img_ratio:
            # Frame is wider: Crop Top/Bottom
            target_h = img_w / frame_ratio
            crop_amount = (img_h - target_h) / img_h
            pic.crop_top = crop_amount / 2
            pic.crop_bottom = crop_amount / 2
        else:
            # Frame is taller: Crop Left/Right
            target_w = img_h * frame_ratio
            crop_amount = (img_w - target_w) / img_w
            pic.crop_left = crop_amount / 2
            pic.crop_right = crop_amount / 2
            
        # Resize to fill box
        pic.left, pic.top, pic.width, pic.height = l, t, w, h

    else:
        # --- CONTAIN (Fit Inside) --- 
        # We need to center the image inside the box without stretching
        if frame_ratio > img_ratio:
            # Frame is wider than image: Fit to Height
            new_w = h * img_ratio
            left_offset = (w - new_w) / 2
            pic.height = h
            pic.width = int(new_w)
            pic.left = l + int(left_offset)
            pic.top = t
        else:
            # Frame is taller than image: Fit to Width
            new_h = w / img_ratio
            top_offset = (h - new_h) / 2
            pic.width = w
            pic.height = int(new_h)
            pic.left = l
            pic.top = t + int(top_offset)



def add_table(slide, el):
    csv_path = ASSETS_DIR / el["source"]
    
    if not csv_path.exists():
        return

    with open(csv_path, newline='', encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if not rows: return

    n_rows = len(rows)
    n_cols = max(len(r) for r in rows) # Safety max
    l, t, w, h = n2pt(el["x"], el["y"], el["width"], el["height"])

    table = slide.shapes.add_table(n_rows, n_cols, l, t, w, h).table

    # Basic styling
    for r in range(n_rows):
        for c in range(len(rows[r])): # specific row length
            cell = table.cell(r, c)
            cell.text = rows[r][c]
            # Optional: Add small font for tables so they fit
            for paragraph in cell.text_frame.paragraphs:
                paragraph.font.size = Pt(12)

def assemble_slide(prs, slide_json, bg_path):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    

    apply_background(slide, bg_path)

    sorted_elements = sorted(slide_json["elements"], key=lambda x: x.get("z", 0))

    for el in slide_elements:
        if el["type"] == "text":
            add_text(slide, el)
        elif el["type"] == "image":
            add_image(slide, el)
        elif el["type"] == "table":
            add_table(slide, el)
            

