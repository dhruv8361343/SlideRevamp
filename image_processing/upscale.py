import subprocess
import sys
from pathlib import Path
import time


def upscale_image(image_path, output_dir):
    """
    Upscale image using Real-ESRGAN and return actual output path.
    """

    REAL_ESRGAN_DIR = Path("Real-ESRGAN").resolve()

    image_path = Path(image_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run Real-ESRGAN
    cmd = [
        sys.executable,
        "inference_realesrgan.py",
        "-n", "RealESRGAN_x4plus",
        "-i", str(image_path),
        "-o", str(output_dir),
        "--ext", "png"
    ]

    subprocess.run(cmd, cwd=REAL_ESRGAN_DIR, check=True)

    # Wait for filesystem
    time.sleep(1)

    # 1️⃣ Check intended output directory
    candidates = list(output_dir.glob("*"))

    if candidates:
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return candidates[0]

    # 2️⃣ FALLBACK: check Real-ESRGAN default results folder
    fallback_dir = REAL_ESRGAN_DIR / "results"
    fallback_files = list(fallback_dir.glob("**/*"))

    if fallback_files:
        fallback_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return fallback_files[0]

    # 3️⃣ If still nothing → real failure
    raise RuntimeError("Real-ESRGAN ran but no output file was found")
