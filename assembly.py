from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import csv
from PIL import Image
import os

prs = Presentation()


ASSETS_DIR = Path("/kaggle/working/outputs")



def n2pt(x, y, w, h):
    return (
        int(x * prs.slide_width),
        int(y * prs.slide_height),
        int(w * prs.slide_width),
        int(h * prs.slide_height)
    )

def add_text(slide, el):
    l, t, w, h = n2pt(el["x"], el["y"], el["width"], el["height"])
    
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    
    # 1. Alignment Mapping
    align_map = {
        "left": PP_ALIGN.LEFT,
        "center": PP_ALIGN.CENTER,
        "right": PP_ALIGN.RIGHT,
        "justify": PP_ALIGN.JUSTIFY
    }
    # Default to Left if not found
    layout_align = el.get("style", {}).get("align", "left")
    align_enum = align_map.get(layout_align, PP_ALIGN.LEFT)

    content_data = el.get("content", [])

    # Legacy check for simple strings
    if isinstance(content_data, str):
        p = tf.paragraphs[0]
        p.text = content_data
        p.alignment = align_enum
        return

    # 2. Iterate Paragraphs
    for i, para_data in enumerate(content_data):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align_enum
        
        # 3. Iterate Runs
        for run_data in para_data:
            run = p.add_run()
            run.text = run_data.get("text", "")
            
            font = run.font
            if run_data.get("bold"): font.bold = True
            if run_data.get("italic"): font.italic = True
            if run_data.get("underline"): font.underline = True
            
            # Size
            extracted_size = run_data.get("font_size_pt")
            layout_default = el.get("font_size", 18)
            # Use extracted size if valid, else layout rule
            final_size = extracted_size if extracted_size else layout_default
            font.size = Pt(final_size)
            
            # Color
            hex_color = run_data.get("color_rgb")
            if hex_color:
                try:
                    font.color.rgb = RGBColor.from_string(str(hex_color).replace("#", ""))
                except:
                    pass
                    




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

    sorted_elements = sorted(slide_json["elements"], key=lambda x: x.get("z", 0)

    for el in slide_json["elements"]:
        if el["type"] == "text":
            add_text(slide, el)
        elif el["type"] == "image":
            add_image(slide, el)
        elif el["type"] == "table":
            add_table(slide, el)
            

