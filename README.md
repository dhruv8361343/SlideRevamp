# SlideRevamp

## link for daily log file : https://docs.google.com/document/d/1fgdK756dCaBX_L8zydD_j4TovyWBluuUPhGvj8ZX3es/edit?usp=sharing

## link for kaggle notebook for using this and instructions for using the notebook are given in the notebook:https://www.kaggle.com/code/dhruv836/slide-revamp

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
steps:   5%|▊               | 100/2000 [00:57<18:14,  1.74it/s, avr_loss=0.0725]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00000100.safetensors
steps:  10%|█▌              | 200/2000 [01:54<17:08,  1.75it/s, avr_loss=0.0715]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00000200.safetensors
steps:  15%|██▍             | 300/2000 [02:51<16:12,  1.75it/s, avr_loss=0.0766]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00000300.safetensors
steps:  20%|███▏            | 400/2000 [03:48<15:14,  1.75it/s, avr_loss=0.0747]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00000400.safetensors
steps:  25%|████            | 500/2000 [04:45<14:17,  1.75it/s, avr_loss=0.0722]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00000500.safetensors
steps:  30%|█████            | 600/2000 [05:42<13:18,  1.75it/s, avr_loss=0.074]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00000600.safetensors
steps:  35%|█████▉           | 700/2000 [06:39<12:22,  1.75it/s, avr_loss=0.072]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00000700.safetensors
steps:  40%|██████▍         | 800/2000 [07:37<11:26,  1.75it/s, avr_loss=0.0719]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00000800.safetensors
steps:  45%|███████▏        | 900/2000 [08:35<10:29,  1.75it/s, avr_loss=0.0717]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00000900.safetensors
steps:  50%|███████▌       | 1000/2000 [09:32<09:32,  1.75it/s, avr_loss=0.0723]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001000.safetensors
steps:  55%|████████▎      | 1100/2000 [10:30<08:35,  1.75it/s, avr_loss=0.0717]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001100.safetensors
steps:  60%|█████████      | 1200/2000 [11:27<07:38,  1.75it/s, avr_loss=0.0714]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001200.safetensors
steps:  65%|█████████▊     | 1300/2000 [12:24<06:40,  1.75it/s, avr_loss=0.0716]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001300.safetensors
steps:  70%|██████████▌    | 1400/2000 [13:21<05:43,  1.75it/s, avr_loss=0.0723]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001400.safetensors
steps:  75%|███████████▎   | 1500/2000 [14:18<04:46,  1.75it/s, avr_loss=0.0722]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001500.safetensors
steps:  80%|████████████   | 1600/2000 [15:15<03:48,  1.75it/s, avr_loss=0.0712]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001600.safetensors
steps:  85%|████████████▊  | 1700/2000 [16:13<02:51,  1.75it/s, avr_loss=0.0712]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001700.safetensors
steps:  90%|█████████████▌ | 1800/2000 [17:10<01:54,  1.75it/s, avr_loss=0.0708]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001800.safetensors
steps:  95%|██████████████▎| 1900/2000 [18:06<00:57,  1.75it/s, avr_loss=0.0708]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00001900.safetensors
steps: 100%|███████████████| 2000/2000 [19:03<00:00,  1.75it/s, avr_loss=0.0702]
saving checkpoint: /kaggle/working/kohya_ss/kohya_ss/outputs/background_generator-step00002000.safetensors
steps: 100%|███████████████| 2000/2000 [19:04<00:00,  1.75it/s, avr_loss=0.0702]
```
<img width="1410" height="770" alt="Image" src="https://github.com/user-attachments/assets/9c53404b-7382-4192-9040-da2bc1c0f793" />

### (23-29 jan)
created script for generating synthetic data for layout generator

creating script to convert output of pptx_extractor.py as per the input of layout generator

create real data by running my scripts on real ppts

train layout generator with 6 outputs

created scripts to assemble the ppt (assembly.py) to check the redesigned ppt with less no. of layouts


### (30-5 jan)
increase the no. of layout outputs to 16

retrain the layout generator with 16 layouts

loss of test set and validation set respectively
 ```python
[0]	validation_0-mlogloss:2.72086	validation_1-mlogloss:2.73958
[50]	validation_0-mlogloss:1.45772	validation_1-mlogloss:1.84872
[100]	validation_0-mlogloss:0.96920	validation_1-mlogloss:1.44070
[150]	validation_0-mlogloss:0.69202	validation_1-mlogloss:1.15627
[200]	validation_0-mlogloss:0.52421	validation_1-mlogloss:0.95506
[250]	validation_0-mlogloss:0.41569	validation_1-mlogloss:0.79912
[299]	validation_0-mlogloss:0.34583	validation_1-mlogloss:0.67543
```


<img width="878" height="701" alt="Image" src="https://github.com/user-attachments/assets/975afe62-7c4c-4ae3-82e3-45383732b482" />

make the script to assemble slide 

check and improve the outputs







