import subprocess
import sys
from pathlib import Path
import shutil

U2NET_DIR = Path("/kaggle/working/U-2-Net")
INPUT_DIR = U2NET_DIR / "test_data" / "test_images"
RESULTS_DIR = U2NET_DIR / "test_data" / "u2net_results"


def generate_mask(image_path, output_dir):
    image_path = Path(image_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1️⃣ Clear input folder
    for f in INPUT_DIR.glob("*"):
        f.unlink()

    # 2️⃣ Copy input image
    temp_image = INPUT_DIR / image_path.name
    shutil.copy(image_path, temp_image)

    # 3️⃣ Run U-2-Net
    subprocess.run(
        [sys.executable, "u2net_test.py"],
        cwd=U2NET_DIR,
        check=True
    )

    # 4️⃣ EXPECTED output mask
    expected_mask = RESULTS_DIR / f"{image_path.stem}.png"

    if not expected_mask.exists():
        raise RuntimeError(
            f"Expected U-2-Net mask not found: {expected_mask}"
        )

    # 5️⃣ Copy to pipeline folder
    final_mask = output_dir / expected_mask.name
    shutil.copy(expected_mask, final_mask)

    return final_mask

