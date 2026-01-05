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


def apply_background(prs, slide, bg_path):
    slide_width = prs.slide_width
    slide_height = prs.slide_height

    slide.shapes.add_picture(
        str(bg_path),
        0,
        0,
        slide_width,
        slide_height
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
                
def apply_run_color(font, run_data, el):
    # order of priority
    # 1. run explicit color
    # 2. element inherited color
    # 3. leave default

    val = (
        (run_data.get("color_rgb") if isinstance(run_data, dict) else None)
        or run_data.get("font_color") if isinstance(run_data, dict) else None
        or el.get("font_color")
    )

    if not val:
        return

    try:
        # CASE 1: already RGBColor object
        if hasattr(val, 'rgb'):
            font.color.rgb = val
            return

        # CASE 2: integer like 16711680
        if isinstance(val, int):
            r = (val >> 16) & 0xFF
            g = (val >> 8) & 0xFF
            b = val & 0xFF
            font.color.rgb = RGBColor(r, g, b)
            return

        # CASE 3: hex string
        clean = str(val).replace("#", "").strip()
        font.color.rgb = RGBColor.from_string(clean)

    except Exception:
        # fallback default
        font.color.rgb = RGBColor(0, 0, 0)


                
from pptx.enum.text import MSO_AUTO_SIZE 

def add_text(slide, el):
    # expand usable content area automatically
    l, t, w, h = n2pt(el["x"], el["y"], el["width"], el["height"])

    box = slide.shapes.add_textbox(l, t, w, h)

    tf = box.text_frame
    tf.word_wrap = True
    
    tf.auto_size = MSO_AUTO_SIZE.SHAPE_TO_FIT_TEXT 

    content_data = el.get("content", []) 
    alignment_map = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}
    align_enum = alignment_map.get(el.get("align", "left"), PP_ALIGN.LEFT)
    

    for i, para_data in enumerate(content_data):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align_enum

        ls = el.get("line_spacing")
        if ls:
            p.line_spacing = ls

        
        if isinstance(para_data, dict):
            p.level = para_data.get("level", 0)
            runs_to_process = para_data.get("runs", [])
            if para_data.get("is_bullet", False):
                enable_bullets(p)
        else:
            # If para_data is just a list of runs directly
            runs_to_process = para_data
        
        
        for run_data in runs_to_process:
            run = p.add_run()
            
            
            if isinstance(run_data, str):
                run.text = run_data
                font = run.font
                apply_run_color(font, run_data, el)

            
            else:
                run.text = run_data.get("text", "")
                font = run.font
                if run_data.get("bold"): font.bold = True
                    
                apply_run_color(font, run_data, el)


            # Apply font size (either from run, element, or default 18)
            size = 18
            if isinstance(run_data, dict):
                size = run_data.get("font_size") or el.get("font_size", 18)
            else:
                size = el.get("font_size", 18)
            font.size = Pt(size)



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

    if el.get("width", 0) > 0.9 and el.get("height", 0) > 0.9:
        slide.shapes.add_picture(str(image_path), 0, 0, prs.slide_width, prs.slide_height)
        return
    
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
    

    apply_background(prs, slide, bg_path)


    sorted_elements = sorted(slide_json["elements"], key=lambda x: x.get("z", 0))

    for el in sorted_elements:
        if el["type"] == "text":
            add_text(slide, el)
        elif el["type"] == "image":
            add_image(slide, el)
        elif el["type"] == "table":
            add_table(slide, el)
            

