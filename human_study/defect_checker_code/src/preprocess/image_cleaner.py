# 이미지 전처리 (리사이즈 등)

import cv2
import os
from pathlib import Path

def resize_and_clean_image(input_path, output_path, size=(512, 512)):
    img = cv2.imread(str(input_path))
    img = cv2.resize(img, size)
    cv2.imwrite(str(output_path), img)

def preprocess_folder(input_dir, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for img_path in Path(input_dir).glob("*.[jp][pn]g"):
        output_path = Path(output_dir) / img_path.name
        resize_and_clean_image(img_path, output_path)

if __name__ == "__main__":
    preprocess_folder("data/raw", "data/processed")
