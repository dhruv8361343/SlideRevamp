### SlideRevamp

link for daily log file : https://docs.google.com/document/d/1fgdK756dCaBX_L8zydD_j4TovyWBluuUPhGvj8ZX3es/edit?usp=sharing
## Timeline and descripiton of work done (actual followed)
# (8-13 jan)
read this documenatation of python-pptx library to extract an ppt
https://python-pptx-fix.readthedocs.io/en/stable/user/intro.html

wrote and understand some functions and comlpeted the script to extract text ,images and different things and add them in respective folders in the form of json format(messy one) (python_extractor.py)

read the code to call the gemini via API
https://ai.google.dev/gemini-api/docs/quickstart
wrote the prompt that is to be given with the output from python_extractor.py to LLM and completed the script/code for content refinement (content_refinement.py).
(LLM will also give the detailed prompt that is to be given to stable diffusion v1.5 for background generation as per the prompt given by user)

# (15-21 jan)
install and run the Real-ESRGAN AND U-2-NET model
created scripts to use them on extracted images(upsclae.py mask.py smart_crop.py process_image.py)
created dateset for finetuning stable diffusion v1.5 (for background generation ) 
fine tune stable stable diffusion v1.5  using LoRA on kohya_ss notebook



