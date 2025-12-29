import cv2
from pathlib import Path

from image_processing.upscale import upscale_image
from image_processing.mask import generate_mask
from image_processing.smart_crop import smart_crop




def process_image(image_path):
    """
    using models for enhancing image
    """
    # Directories
UPSCALED_DIR = Path("/kaggle/working/outputs/images_upscaled")
MASKS_DIR = Path("/kaggle/working/outputs/masks")
FINAL_DIR = Path("/kaggle/working/outputs/images_final")

# Ensure output dirs exist
UPSCALED_DIR.mkdir(parents=True, exist_ok=True)
MASKS_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DIR.mkdir(parents=True, exist_ok=True)
    

   # Upscale (Real-ESRGAN)
    upscaled_path = upscale_image(
        image_path=image_path,
        output_dir=UPSCALED_DIR
    )
    


   #  Generate U-2-Net mask
    mask_path = generate_mask(
        image_path=upscaled_path,
        output_dir=MASKS_DIR
    )

   #  Smart crop
    final_img = smart_crop(
        image_path=str(upscaled_path),
        mask_path=str(mask_path),
        target_ratio=16/9
    )


    #  Save final image
    final_out = FINAL_DIR / img_path.name
    cv2.imwrite(str(final_out), final_img)

    return final_out


