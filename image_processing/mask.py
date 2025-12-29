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

#U-2-NET doesn't allow mdoel 2 run from external path so we have to first copy our input in their test folder and then copy the results from their folder
    for f in INPUT_DIR.glob("*"):
        f.unlink()

    
    temp_image = INPUT_DIR / image_path.name
    shutil.copy(image_path, temp_image)

    subprocess.run(
        [sys.executable, "u2net_test.py"],
        cwd=U2NET_DIR,
        check=True
    )

    
    expected_mask = RESULTS_DIR / f"{image_path.stem}.png"

    if not expected_mask.exists():
        raise RuntimeError(
            f"Expected U-2-Net mask not found: {expected_mask}"
        )

    final_mask = output_dir / expected_mask.name
    shutil.copy(expected_mask, final_mask)

    return final_mask


