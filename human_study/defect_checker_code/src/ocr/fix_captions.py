# 오탈자 수정 코드드

import pandas as pd

# ✅ 1. 교정할 단어 사전 (필요할 때 계속 추가하면 됨)
# 후처리 코드 대신 api로 오타 교정
corrections = {
    "미름함": "미흡함",
    "좌츰" : "좌측",
    "도어오염": "도어 오염",
    "스프랑클러": "스프링클러",
    "들듬": "들뜸",
    "칭틀": "창틀",
    "등": "조명등"
    # 계속 추가 가능...
}

# ✅ 2. 교정 함수 정의
def correct_caption(text: str) -> str:
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    return text.strip()

# ✅ 3. CSV 불러오기
df = pd.read_csv("data/train_caption.csv")

# ✅ 4. 캡션 교정 적용
df["caption"] = df["caption"].apply(correct_caption)

# ✅ 5. 새 파일로 저장
df.to_csv("data/train_caption.csv", index=False, encoding="utf-8-sig")

print("✅ 교정 완료: data/train_caption.csv 로 저장됨")

