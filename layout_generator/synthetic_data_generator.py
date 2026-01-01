import pandas as pd
import numpy as np
import random

SAMPLES_PER_CLASS = 3000
OUTPUT_FILE = "synthetic_layout_dataset.csv"
SEED = 42

np.random.seed(SEED)
random.seed(SEED)


# Layout labels (16 Classes)
 
LAYOUT_CLASSES = {
    0: "text_only",
    1: "title_center",
    2: "two_column",
    3: "three_column",
    4: "four_column",
    5: "image_left",
    6: "image_right",
    7: "image_top",
    8: "image_bottom",
    9: "image_grid",
    10: "image_background",
    11: "big_stat",
    12: "quote",
    13: "timeline",
    14: "table_center",
    15: "agenda"
}





def generate_row(layout_id):
    """
    Creates a row of features 
    """
    row = {}
    
    # Defaults (Clean slate)
    
    row["num_text_blocks"] = 1
    row["total_text_length"] = 100
    row["avg_text_len"] = 0
    row["num_images"] = 0
    row["largest_image_area"] = 0.0
    row["avg_image_area"] = 0.0
    row["img_aspect_ratio"] = 0.0
    row["has_table"] = 0
    row["has_quote"] = 0
    row["has_digits"] = 0
    row["is_agenda"] = 0
    row["slide_density"] = 0
    row["source"] = "synthetic"

    # 
    
    if layout_id == 14: # table_center
        row["has_table"] = 1
        row["num_text_blocks"] = np.random.randint(0, 3)
        row["total_text_length"] = np.random.randint(50, 200)

    elif layout_id == 15: # agenda
        row["is_agenda"] = 1
        row["num_text_blocks"] = np.random.randint(3, 8) 
        row["total_text_length"] = np.random.randint(100, 500)

    elif layout_id == 12: # quote
        row["has_quote"] = 1
        row["num_images"] = np.random.choice([0, 1]) 
        row["total_text_length"] = np.random.randint(50, 300)
        if row["num_images"] == 1:
            row["img_aspect_ratio"] = 1.0
            row["largest_image_area"] = 0.1

    elif layout_id == 11: # big_stat
        row["has_digits"] = 1
        row["total_text_length"] = np.random.randint(10, 80) # Very short
        row["num_text_blocks"] = np.random.randint(1, 3) # Number + Caption

    elif layout_id == 1: # title_center
        # Must be short text, 0 images
        row["total_text_length"] = np.random.randint(20, 140) 
        row["num_text_blocks"] = 1

    elif layout_id == 0: # text_only
        # Must be longer text to avoid 'title_center'
        row["total_text_length"] = np.random.randint(350, 800)
        row["num_text_blocks"] = 1 # Single block body

    elif layout_id == 2: # two_column
        row["num_text_blocks"] = 2
        row["total_text_length"] = np.random.randint(300, 800)

    elif layout_id == 3: # three_column
        row["num_text_blocks"] = 3
        row["total_text_length"] = np.random.randint(300, 900)

    elif layout_id == 4: # four_column
        row["num_text_blocks"] = 4
        row["total_text_length"] = np.random.randint(400, 1000)

    elif layout_id == 13: # timeline
        row["num_text_blocks"] = np.random.randint(5, 8) # 5+ blocks usually implies timeline
        row["total_text_length"] = np.random.randint(300, 800)

    elif layout_id == 10: # image_background
        row["num_images"] = 1
        # Must have low text to trigger Background mode
        row["total_text_length"] = np.random.randint(50, 180)
        row["largest_image_area"] = 1.0 # Full screen implies BG

    elif layout_id == 7: # image_top
        row["num_images"] = 1
        row["img_aspect_ratio"] = np.random.uniform(1.7, 2.5) # Wide
        row["total_text_length"] = np.random.randint(250, 600) # 
        row["largest_image_area"] = 0.4

    elif layout_id == 8: # image_bottom
        row["num_images"] = 1
        row["img_aspect_ratio"] = np.random.uniform(1.7, 2.5) # Wide
        row["total_text_length"] = np.random.randint(250, 600)
        row["largest_image_area"] = 0.4

    elif layout_id == 5: # image_left
        row["num_images"] = 1
        row["img_aspect_ratio"] = np.random.uniform(0.6, 1.4) # Tall/Square
        row["total_text_length"] = np.random.randint(200, 800)
        row["largest_image_area"] = 0.4

    elif layout_id == 6: # image_right
        row["num_images"] = 1
        row["img_aspect_ratio"] = np.random.uniform(0.6, 1.4) # Tall/Square
        row["total_text_length"] = np.random.randint(200, 800)
        row["largest_image_area"] = 0.4

    elif layout_id == 9: # image_grid
        row["num_images"] = np.random.randint(2, 6)
        row["avg_image_area"] = 0.2
    
    # Derived Features
    row["avg_text_len"] = row["total_text_length"] / row["num_text_blocks"] if row["num_text_blocks"] > 0 else 0
    row["slide_density"] = round((row["num_text_blocks"] + row["num_images"]) / 10.0, 2)
    row["layout_class_numeric"] = layout_id

    
    if row["num_images"] > 0:
        row["img_aspect_ratio"] += np.random.normal(0, 0.05)
        
    return row



all_data = []
print(f"Generating balanced dataset ({SAMPLES_PER_CLASS} per class)...")

for class_id in range(16):
    print(f"  - Generating class {class_id}: {LAYOUT_CLASSES[class_id]}...")
    for _ in range(SAMPLES_PER_CLASS):
        sample = generate_row(class_id)
        all_data.append(sample)

# Shuffle dataset so training doesn't see all 'text_only' first
random.shuffle(all_data)


# save to CSV 
df = pd.DataFrame(all_data)

# Add string label for verification
df["layout_class"] = df["layout_class_numeric"].map(LAYOUT_CLASSES)

df.to_csv(OUTPUT_FILE, index=False)

print(f" Success! Saved {len(df)} samples to {OUTPUT_FILE}")
print(" Verification of Distribution:")
print(df["layout_class_name"].value_counts())