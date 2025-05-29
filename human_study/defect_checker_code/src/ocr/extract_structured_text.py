import json
from pathlib import Path

# ✅ bbox 기반 줄 정렬 + key-value 추출
def extract_key_value_by_row(results, row_threshold=15):
    items = []
    for r in results:
        vertices = r['boundingPoly']['vertices']
        top = min(p["y"] for p in vertices)
        left = min(p["x"] for p in vertices)
        items.append({
            "text": r["inferText"].strip(),
            "top": top,
            "left": left,
            "bbox": vertices
        })

    # y 기준 정렬 → 줄 그룹 만들기
    items.sort(key=lambda x: (x["top"], x["left"]))
    rows = []
    current_row = []

    for item in items:
        if not current_row:
            current_row.append(item)
            continue
        if abs(item["top"] - current_row[0]["top"]) <= row_threshold:
            current_row.append(item)
        else:
            rows.append(sorted(current_row, key=lambda x: x["left"]))
            current_row = [item]

    if current_row:
        rows.append(sorted(current_row, key=lambda x: x["left"]))

    # key-value 추출
    pairs = []
    for row in rows:
        if len(row) >= 2:
            key = row[0]["text"].replace(" ", "")
            value = " ".join([x["text"] for x in row[1:]])
            pairs.append((key, value))
        elif len(row) == 1:
            key = row[0]["text"].replace(" ", "")
            pairs.append((key, ""))

    return pairs

# ✅ JSON → TXT 변환
def convert_all_json_to_txt(json_folder, output_folder):
    json_folder = Path(json_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    for json_file in json_folder.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # CLOVA OCR 포맷 대응
        pairs = extract_key_value_by_row(data["raw"])

        txt_path = output_folder / f"{json_file.stem}.txt"
        with open(txt_path, 'w', encoding='utf-8') as out:
            for key, value in pairs:
                out.write(f"{key} : {value}\n")
        print(f"✅ 저장 완료: {txt_path.name}")

# 실행
if __name__ == "__main__":
    convert_all_json_to_txt("data/ocr_texts3", "data/ocr_texts_structured3")
