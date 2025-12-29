import cv2
from pathlib import Path

from image_processing.upscale import upscale_image
from image_processing.mask import generate_mask
from image_processing.smart_crop import smart_crop


def process_image(image_path):
    """
    using models for enhancing image
    """

    image_path = Path(image_path)

    # 1. Upscale
    upscaled = upscale_image(
    image_path,
    "week2_assets/images_upscaled"
)


    # 2. Generate mask
    mask = generate_mask(
        image_path=upscaled,
        output_dir="week2_assets/masks"
    )

    # 3. Smart crop (always)
    final_img = smart_crop(
        image_path=str(upscaled),
        mask_path=str(mask),
        target_ratio=16/9
    )

    # 4. Save final image
    out_dir = Path("week2_assets/images_final")
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / image_path.name
    cv2.imwrite(str(out_path), final_img)

    return out_path

