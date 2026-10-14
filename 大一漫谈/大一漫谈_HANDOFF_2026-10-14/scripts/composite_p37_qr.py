"""Rebuild P37 from the AI-drawn empty frame and the user's real QR pixels.

This script does not synthesize or redraw QR content. It places the exact user-provided
QR image (downsampled without editing its modules) into the reserved white area.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "drafts/P37_寄语_留白框原生底图.png"
QR = ROOT / "assets/wechat_qr.png"
OUTPUT = ROOT / "deliverables/P37_寄语与真实微信二维码_成品.png"
SIZE = (1920, 1080)
# Bounding box of the white scan area in the 1920 x 1080 version of BASE.
WHITE_RECT = (1276, 361, 1737, 847)
QR_SIDE = 420


def make_slide() -> None:
    with Image.open(BASE) as im:
        slide = ImageEnhance.Sharpness(
            im.convert("RGB").resize(SIZE, Image.Resampling.LANCZOS)
        ).enhance(1.08)
    with Image.open(QR) as im:
        qr = im.convert("RGB").resize((QR_SIDE, QR_SIDE), Image.Resampling.LANCZOS)
    ImageDraw.Draw(slide).rectangle(WHITE_RECT, fill="white")
    x = (WHITE_RECT[0] + WHITE_RECT[2] - QR_SIDE) // 2
    y = (WHITE_RECT[1] + WHITE_RECT[3] - QR_SIDE) // 2
    slide.paste(qr, (x, y))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    slide.save(OUTPUT, format="PNG", optimize=True)

    detector = cv2.QRCodeDetector()
    source = cv2.imread(str(QR))
    source = cv2.copyMakeBorder(source, 70, 70, 70, 70, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    original_payload, _, _ = detector.detectAndDecode(source)
    final_payload, _, _ = detector.detectAndDecode(cv2.cvtColor(np.array(slide), cv2.COLOR_RGB2BGR))
    if not original_payload or not final_payload or original_payload != final_payload:
        raise RuntimeError("QR decoding failed or changed: do not release this slide until a real phone scan passes.")
    print(f"Saved {OUTPUT} ({SIZE[0]}x{SIZE[1]}); QR payload matches the original image.")


if __name__ == "__main__":
    make_slide()
