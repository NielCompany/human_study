# 사진을 불러오고 텍스트만 추출(easyocr 사용)해서 json파일로 저장 
import requests
import os
import uuid
import time
import json
from pathlib import Path
from collections import OrderedDict
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
CLOBA_API_KEY = os.getenv("CLOBA_API_KEY")

# ✅ CLOVA OCR 설정
API_URL = 'https://2cphq1vxd0.apigw.ntruss.com/custom/v1/42151/a1af5c2a61e3b09e3f2d750b86dd3d4b58e873f8a3bcdbe138c95b6d24e5cc7c/general'  # 실제 값으로 교체
SECRET_KEY = CLOBA_API_KEY  # 실제 키로 교체
INPUT_DIR = Path("data/samples3")
OUTPUT_DIR = Path("data/ocr_texts3")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ✅ 키워드 정의 및 표준화
KEYWORDS = ["현장명", "공종", "위치", "내용", "일자", "기타", "상세내용"]
KEYWORD_ALIASES = {
    "공사명": "현장명",
    "공 종": "공종",
    "공종": "공종",
    "위 치": "위치",
    "위치": "위치",
    "내 용": "내용",
    "내용": "내용",
    "일 자": "일자",
    "일자": "일자",
    "기타": "기타",
    "상세 내용": "상세내용"
}

def normalize_keyword(keyword: str) -> str:
    return KEYWORD_ALIASES.get(keyword.replace(" ", ""), keyword.replace(" ", ""))

def run_ocr(image_path: Path):
    request_json = {
        'images': [{'format': image_path.suffix[1:], 'name': image_path.name}],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }
    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [('file', open(image_path, 'rb'))]
    headers = {'X-OCR-SECRET': SECRET_KEY}

    try:
        response = requests.post(API_URL, headers=headers, data=payload, files=files, timeout=30)
        return response.json()
    except Exception as e:
        print(f"❌ 오류: {image_path.name} - {e}")
        return None

def parse_ocr_response(result_json):
    texts = [f['inferText'].strip() for f in result_json['images'][0]['fields']]
    output = OrderedDict()
    current_key = None
    동호수 = ""

    for text in texts:
        norm_text = normalize_keyword(text)
        if norm_text in KEYWORDS:
            current_key = norm_text
            output[current_key] = ""
        elif "동" in text and "호" in text and current_key == "현장명":
            동호수 = text
        elif current_key:
            output[current_key] += text + " "

    if "현장명" in output and 동호수:
        output["현장명"] = output["현장명"].strip() + " " + 동호수

    return {k: v.strip() for k, v in output.items()}

def main():
    image_paths = sorted([p for p in INPUT_DIR.glob("*") if p.suffix.lower() in [".jpg", ".jpeg", ".png"]])

    for img_path in tqdm(image_paths, desc="🔍 OCR 진행 중"):
        result_json = run_ocr(img_path)
        if result_json:
            parsed = parse_ocr_response(result_json)
            save_path = OUTPUT_DIR / f"{img_path.stem}.json"
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "image": img_path.name,
                    "fields": parsed,
                    "raw": result_json['images'][0]['fields']
                }, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()