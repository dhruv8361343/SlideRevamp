# SlideRevamp

link for daily log file : https://docs.google.com/document/d/1fgdK756dCaBX_L8zydD_j4TovyWBluuUPhGvj8ZX3es/edit?usp=sharing
## Timeline and descripiton of work done (actual followed)
### (8-13 jan)
read this documenatation of python-pptx library to extract an ppt
https://python-pptx-fix.readthedocs.io/en/stable/user/intro.html

wrote and understand some functions and comlpeted the script to extract text ,images and different things and add them in respective folders in the form of json format(messy one) (python_extractor.py)

read the code to call the gemini via API
https://ai.google.dev/gemini-api/docs/quickstart
wrote the prompt that is to be given with the output from python_extractor.py to LLM and completed the script/code for content refinement (content_refinement.py).
(LLM will also give the detailed prompt that is to be given to stable diffusion v1.5 for background generation as per the prompt given by user)

### (15-21 jan)
install and run the Real-ESRGAN AND U-2-NET model

created scripts to use them on extracted images(upsclae.py mask.py smart_crop.py process_image.py)

created dateset for finetuning stable diffusion v1.5 (for background generation ) 

fine tune stable stable diffusion v1.5  using LoRA on kohya_ss notebook

```python 
in GUI 

for fine tuning I set the following parameters to
Train batch size =1

Epoch = 10

Max train steps = 2000

LR Scheduler = cosine

Optimizer = AdamW8bit

Max grad norm = 8

Learninf Rate = 0.0001

LR warmup = 100

LR# cycles = 1

Text Encoder learning rate = 0.0005

Unet learning rate =0.0001

network rank = 16

network alpha = 16

Gredient accumulate steps =1

Save every N steps =100


Keep n tokens =1

Max token length = 75

gradient check pointing = true

shuffle caption = true

(for avoiding over fitting)

Min SNR Gamma = 5

Noise offset = 0.05
'''

### (23-29 jan)
created script for generating synthetic data for layout generator

creating script to convert output of pptx_extractor.py as per the input of layout generator

create real data by running my scripts on real ppts

train layout generator with 6 outputs





