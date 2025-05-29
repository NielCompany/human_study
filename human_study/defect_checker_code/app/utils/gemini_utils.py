# gemini_utils.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일에서 API 키 불러오기
load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되어 있지 않습니다.")

genai.configure(api_key=GEMINI_API_KEY)



# Gemini 모델 선택 (flash 또는 pro 사용 가능)
model = genai.GenerativeModel("gemini-1.5-flash")

def explain_by_gemini(prompt: str) -> str:
    """하자 예측 결과와 키워드를 기반으로 Gemini 설명 생성"""
    response = model.generate_content(prompt)
    # response = model.generate_content(question) 
    return response.text.strip()
