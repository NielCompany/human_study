from paddleocr import PaddleOCR
from pathlib import Path
import json

# PP-OCRv3 기반 설정
ocr = PaddleOCR(
    use_angle_cls=True,          # 글자 방향 교정
    lang='korean',               # 한국어 모델 사용
    det_db_box_thresh=0.5,       # 텍스트 박스 감지 민감도
    rec_algorithm='CRNN',        # 텍스트 인식 알고리즘
    det_algorithm='DB',          # 감지 알고리즘
    use_dilation=True,           # 박스 확장으로 작은 글씨 보정
    show_log=False               # 로그 출력 안 함
)

def run_ocr_on_folder(image_folder, output_folder):
    image_folder = Path(image_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    # 확장자 목록
    image_exts = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]

    for ext in image_exts:
        for img_path in image_folder.glob(ext):
            result_file = output_folder / f"{img_path.stem}.json"
            if result_file.exists():
                print(f"✅ 이미 처리됨: {img_path.name}")
                continue

            print(f"🔍 처리 중: {img_path.name}")
            result = ocr.ocr(str(img_path))[0]

            output = {
                "image": img_path.name,
                "results": []
            }

            for line in result:
                box = line[0]
                text = line[1][0]
                conf = float(line[1][1])

                output["results"].append({
                    "text": text,
                    "bbox": [[int(x), int(y)] for x, y in box],
                    "conf": conf
                })

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_ocr_on_folder("data/samples", "data/paddle_ocr_texts")
