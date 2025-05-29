import pandas as pd
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time
import os
from dotenv import load_dotenv

# gpt 활용 띄어쓰기
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt_fix_spacing(text: str) -> str:
    try:
        prompt = f"""다음 문장에서 **의미는 절대 바꾸지 말고**, **띄어쓰기만** 교정해줘. 따옴표나 문장 부호도 건드리지 마.

        문장: "{text}"
        교정된 문장:"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {"role": "system", "content": "너는 한국어 띄어쓰기 전문가야. 의미는 바꾸지 말고, 띄어쓰기만 교정해."},
                {"role": "user", "content": f"문장: {text}\n교정된 문장:"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❗ 오류 발생: {text} → {e}")
        return text

# CSV 불러오기
df = pd.read_csv("data/train_caption.csv")
corrected = [None] * len(df)
print("🛠 띄어쓰기 교정 중...")

# 병렬 처리
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {
        executor.submit(gpt_fix_spacing, text): idx
        for idx, text in enumerate(df["caption"])
    }

    for future in tqdm(as_completed(futures), total=len(futures)):
        idx = futures[future]
        try:
            corrected[idx] = future.result()
        except:
            corrected[idx] = df["caption"][idx]

# 결과 저장
df["caption"] = corrected
df.to_csv("data/train_caption_corrected.csv", index=False, encoding="utf-8-sig")
print("✅ 완료 → data/train_caption_corrected.csv")
