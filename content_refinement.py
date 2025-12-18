import os
import sys
import json
import glob
import csv
from google import genai
from google.genai import types
#from dotenv import load_dotenv
# if want to run locally
# loading api key from .env file
#load_dotenv()
#api_key = os.getenv("GEMINI_API_KEY")



# for running it on kaggle
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
api_key= user_secrets.get_secret("GEMINI_API_KEY")

if not api_key:
    print("no api key found")
    sys.exit(1)


 

#  to get the data from the extracted json and give it to llm for refinement
def load_and_clean_slides(ingestion_output_dir):
    """
    Reads extracted slide JSON + table CSV.
    Returns structured slide-wise content for LLM.
    """
    slides = []

    pattern = os.path.join(ingestion_output_dir, "slide_*", "*_metadata.json")
    files = sorted(glob.glob(pattern))

    if not files:
        print(" No slide metadata found.")
        return None

    for file_path in files:
        slide_dir = os.path.dirname(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        slide_num = data.get("slide_num")
        blocks = []

        for shape in data.get("shapes", []):

            #text block
            if shape.get("has_text") and shape.get("text"):
                text = shape["text"].strip()
                if text:
                    blocks.append({
                        "type": "text",
                        "text": text
                    })

            #table 
            elif shape.get("has_table"):
                csv_rel = shape.get("table_csv")
                if csv_rel:
                    csv_name = os.path.basename(csv_rel)
                    csv_path = os.path.join(slide_dir, csv_name)

                    if os.path.exists(csv_path):
                        rows = []
                        with open(csv_path, "r", encoding="utf-8") as csvfile:
                            reader = csv.reader(csvfile)
                            for row in reader:
                                rows.append(" | ".join(row))

                        blocks.append({
                            "type": "table",
                            "data": " || ".join(rows)
                        })
                    else:
                        blocks.append({
                            "type": "table",
                            "data": "TABLE_PRESENT_BUT_MISSING"
                        })

            # image
            elif shape.get("has_image"):
                blocks.append({
                    "type": "image",
                    "note": "Image asset present"
                })

            #complex
            elif shape.get("problem"):
                blocks.append({
                    "type": "complex_visual",
                    "note": shape.get("problem")
                })

        slides.append({
            "slide_num": slide_num,
            "content_blocks": blocks
        })

    return slides

 
# style and content reifnement (prompt for llm)


def generate_style_token(user_vibe, slides):
    """
    Converts vibe + structured slides into a Style Token
    with refined  content.
    """

    system_instruction = """
You are the Style Orchestrator for a PPT Redesign System.


### ABSOLUTE RULES:
- DO NOT summarize content
- DO NOT remove information
- DO NOT invent new facts
- Preserve all tables exactly
- Fix grammar, clarity, tone only
- Keep content strictly slide-wise

### TEXT REFINEMENT RULES:
- Improve wording while preserving meaning
- Break long paragraphs into readable blocks
- Maintain bullet-style formatting where applicable

### TABLE RULES:
- Never modify numbers or structure
- Do not rewrite tables into text

### OUTPUT FORMAT:
Return ONLY valid JSON (no markdown).

{
  "style_name": "string",
  "color_palette": ["#hex1", "#hex2", "#hex3", "#hex4", "#hex5"],
  "font_pair": {
    "title": "Google Font Name",
    "body": "Google Font Name"
  },
  "background_prompt": "Stable Diffusion v1.5 background prompt",
  "slides": [
    {
      "slide_num": number,
      "layout_suggestion": "Title Only | Two Column | Image Left | Big Number | Table Focus",
      "content_blocks": [
        {
          "type": "text | table | image | complex_visual",
          "text": "only if text",
          "data": "only if table",
          "note": "only if image/complex"
        }
      ]
    }
  ]
}
"""

    client = genai.Client()

    user_prompt = {
        "user_vibe": user_vibe,
        "slides": slides
    }

    

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=json.dumps(user_prompt),
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.4,
            max_output_tokens=8192
        )
    )
    
    return json.loads(response.candidates[0].content.parts[0].text)


# for testing this file
if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python style_orchestrator.py <INGESTION_FOLDER>")
        sys.exit(1)

    ingestion_folder = sys.argv[1]

    if not os.path.exists(ingestion_folder):
        print("Ingestion folder not found.")
        sys.exit(1)

    slides = load_and_clean_slides(ingestion_folder)

    if not slides:
        print("Failed to load slides.")
        sys.exit(1)

    USER_VIBE = "Futuristic Cyberpunk, Neon Blue & Purple, High Tech, Dark Mode"

    style_token = generate_style_token(USER_VIBE, slides)

    output_path = os.path.join(ingestion_folder, "style_token.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(style_token, f, indent=4)

    
    print(f"Style token saved at: {output_path}")
