# 텍스트 파일 위치 정보를 제외하고 정리

import re
from pathlib import Path
import csv
import re

# 제거할 위치 관련 단어 리스트 (사물명은 제외)
LOCATION_WORDS = [
    "침실3", "거실", "정면", "측면", "좌측", "우측", "좌족", "우족", "코너", 
    "하단", "상단", "출입구", "입구", "창문", "바닥", "화장실", "안방", "상부", 
    "죄축", "드레스톱", "영어", "하부","좌츰", "주방", "좌축", "통로 "
    "발코니2", "부부욕실", "실외기실", "파우더", "발코니", "발코니1", 
    "대피실", "주방발코니", "공용욕실", "침2", "침3", "현관", "주방발코니", "침실1",
    "드레스룸", "침실", "욕실", "욕실1", "욕실2", "욕실3", "침3", "1", "2", "/", "3", 
]

# 1. OCR에서 추출된 '내용' 텍스트에서 위치 단어 제거
def clean_location_info(text):

    for word in LOCATION_WORDS:
        text = text.replace(word, "")

    return ' '.join(text.split())  # 여러 공백을 하나로 정리

# 2. 하나의 .txt 파일에서 '내용' 항목만 추출 → 정제해서 반환
def make_caption_from_txt(txt_path):
    fields = {}
    with open(txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            if ':' in line:
                key, value = line.strip().split(":", 1)
                fields[key.strip()] = value.strip()

    content = fields.get("하자내용", "")
    cleaned = clean_location_info(content)
    cleaned = cleaned.replace('"', '').replace("'", "") 
    return clean_location_info(content)  # 정제 후 반환

# 3. 숫자 기준으로 이미지 정렬하기 위한 함수 (image1 → image10 순서 보정용)
def extract_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else -1

# 4. 전체 .txt 폴더를 순회하며 image-caption 쌍 만들고, 정렬 후 CSV로 저장
def build_caption_dataset(txt_folder, output_csv):
    txt_folder = Path(txt_folder)
    rows = []

    # 각 .txt 파일에 대해 이미지명 + 캡션 추출
    for txt_file in txt_folder.glob("*.txt"):
        image_name = f"{txt_file.stem}.jpg"
        caption = make_caption_from_txt(txt_file)
        if caption:
            rows.append({"image": image_name, "caption": caption})

    # 이미지 번호 기준으로 정렬 (문자열 정렬 오류 방지)
    rows.sort(key=lambda x: extract_number(x["image"]))

    # CSV 저장
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["image", "caption"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ CSV 저장 완료 (이미지 번호 순): {output_csv}")

# 5. 실행
if __name__ == "__main__":
    build_caption_dataset("data/ocr_texts_structured3", "data/train_caption4.csv")