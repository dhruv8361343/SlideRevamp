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
```
 loss after every 100 steps
```python
steps:   5%|▊               | 100/2000 [00:51<16:10,  1.96it/s, avr_loss=0.0772]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00000100.safetensors
steps:  10%|█▌              | 200/2000 [01:43<15:29,  1.94it/s, avr_loss=0.0774]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00000200.safetensors
steps:  15%|██▍             | 300/2000 [02:38<14:59,  1.89it/s, avr_loss=0.0705]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00000300.safetensors
steps:  20%|███▏            | 400/2000 [03:33<14:12,  1.88it/s, avr_loss=0.0721]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00000400.safetensors
steps:  25%|████▎            | 500/2000 [04:28<13:25,  1.86it/s, avr_loss=0.074]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00000500.safetensors
steps:  30%|████▊           | 600/2000 [05:23<12:34,  1.85it/s, avr_loss=0.0718]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00000600.safetensors
steps:  35%|█████▌          | 700/2000 [06:18<11:42,  1.85it/s, avr_loss=0.0735]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00000700.safetensors
steps:  40%|██████▊          | 800/2000 [07:13<10:49,  1.85it/s, avr_loss=0.071]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00000800.safetensors
steps:  45%|███████▏        | 900/2000 [08:08<09:56,  1.84it/s, avr_loss=0.0706]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00000900.safetensors
steps:  50%|████████▌        | 1000/2000 [09:02<09:02,  1.84it/s, avr_loss=0.07]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001000.safetensors
steps:  55%|████████▊       | 1100/2000 [09:57<08:08,  1.84it/s, avr_loss=0.071]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001100.safetensors
steps:  60%|█████████      | 1200/2000 [10:52<07:14,  1.84it/s, avr_loss=0.0704]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001200.safetensors
steps:  65%|██████████▍     | 1300/2000 [11:47<06:20,  1.84it/s, avr_loss=0.071]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001300.safetensors
steps:  70%|██████████▌    | 1400/2000 [12:42<05:26,  1.84it/s, avr_loss=0.0708]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001400.safetensors
steps:  75%|████████████▊    | 1500/2000 [13:36<04:32,  1.84it/s, avr_loss=0.07]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001500.safetensors
steps:  80%|████████████   | 1600/2000 [14:31<03:37,  1.84it/s, avr_loss=0.0695]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001600.safetensors
steps:  85%|████████████▊  | 1700/2000 [15:26<02:43,  1.83it/s, avr_loss=0.0697]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001700.safetensors
steps:  90%|█████████████▌ | 1800/2000 [16:21<01:49,  1.83it/s, avr_loss=0.0693]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001800.safetensors
steps:  95%|██████████████▎| 1900/2000 [17:16<00:54,  1.83it/s, avr_loss=0.0694]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/models/last-step00001900.safetensors
steps: 100%|███████████████| 2000/2000 [18:11<00:00,  1.83it/s, avr_loss=0.0692]
```
<img width="1410" height="770" alt="Image" src="https://github.com/user-attachments/assets/9c53404b-7382-4192-9040-da2bc1c0f793" />

### (23-29 jan)
created script for generating synthetic data for layout generator

creating script to convert output of pptx_extractor.py as per the input of layout generator

create real data by running my scripts on real ppts

train layout generator with 6 outputs





