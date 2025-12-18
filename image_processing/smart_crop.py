import cv2
import numpy as np


def smart_crop(
    image_path,
    mask_path,
    target_ratio=16/9,
    padding=0.1
):
    """
    Smart crop using U-2-Net mask.

    image_path: upscaled image (Real-ESRGAN output)
    mask_path: U-2-Net binary mask
    target_ratio: width / height
    padding: extra margin around object (10%)
    """

    # Load image & mask
    img = cv2.imread(image_path)
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    h, w = img.shape[:2]

    # Threshold mask
    _, mask = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)

    # Find foreground pixels
    ys, xs = np.where(mask == 255)

    if len(xs) == 0 or len(ys) == 0:
        # fallback: center crop
        return img

    x_min, x_max = xs.min(), xs.max()
    y_min, y_max = ys.min(), ys.max()

    # Add padding
    bw = x_max - x_min
    bh = y_max - y_min
    x_min -= int(bw * padding)
    x_max += int(bw * padding)
    y_min -= int(bh * padding)
    y_max += int(bh * padding)

    # Clamp
    x_min, y_min = max(0, x_min), max(0, y_min)
    x_max, y_max = min(w, x_max), min(h, y_max)

    # Adjust to target aspect ratio
    box_w = x_max - x_min
    box_h = y_max - y_min
    box_ratio = box_w / box_h

    if box_ratio > target_ratio:
        # too wide → expand height
        new_h = int(box_w / target_ratio)
        diff = new_h - box_h
        y_min -= diff // 2
        y_max += diff // 2
    else:
        # too tall → expand width
        new_w = int(box_h * target_ratio)
        diff = new_w - box_w
        x_min -= diff // 2
        x_max += diff // 2

    # Final clamp
    x_min, y_min = max(0, x_min), max(0, y_min)
    x_max, y_max = min(w, x_max), min(h, y_max)

    return img[y_min:y_max, x_min:x_max]
