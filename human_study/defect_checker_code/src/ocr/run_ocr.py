import easyocr
import os
import json
from pathlib import Path

def run_ocr_on_folder(image_folder, output_folder):
    reader = easyocr.Reader(['ko', 'en'])
    image_folder = Path(image_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    for ext in ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]:
        for img_path in image_folder.glob(ext):
            result_file = output_folder / f"{img_path.stem}.json"
            if result_file.exists():
                print(f"✅ 이미 처리됨: {img_path.name}")
                continue  # 이미 처리된 경우 건너뜀

            print(f"🔍 처리 중: {img_path.name}")
            results = reader.readtext(str(img_path))
            output = {
                "image": img_path.name,
                "results": [
                    {
                        "text": text,
                        "bbox": [[int(x), int(y)] for (x, y) in bbox],
                        "conf": float(prob)
                    }
                    for bbox, text, prob in results
                ]
            }
            with open(result_file, "w", encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_ocr_on_folder("data/samples", "data/ocr_texts")
