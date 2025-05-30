# # gemini_utils.py
# import os
# from dotenv import load_dotenv
# import google.generativeai as genai
# from PIL import Image

# # .env 파일에서 API 키 불러오기
# load_dotenv()

# # Gemini API 설정
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되어 있지 않습니다.")

# genai.configure(api_key=GEMINI_API_KEY)


# # 첫 인사 플래그 & 대화 저장
# greeted = False
# conversation_history = []

# # Gemini 모델 선택 (flash 또는 pro 사용 가능)
# model = genai.GenerativeModel("gemini-1.5-flash")

# def explain_by_gemini(prompt: str) -> str:
#     """하자 예측 결과와 키워드를 기반으로 Gemini 설명 생성"""
#     response = model.generate_content(prompt)
#     # response = model.generate_content(question) 
#     return response.text.strip()


import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. 환경 설정
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2. 모델 초기화
llm_model = genai.GenerativeModel("gemini-2.0-flash")

# # 3. 프로필 텍스트 전체 로드
# PROFILE_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../data-files/bot_profile.txt"))
# with open(PROFILE_PATH, "r", encoding="utf-8") as f:
#     profile_text = f.read()

# 4. 첫 인사 플래그 & 대화 저장
greeted = False
conversation_history = []

# 5. 메인 함수
def ask_gemini(question):
    global greeted, conversation_history

    greeting = "" if greeted else "안녕하세요. \n궁금한 내용을 물어보세요!\n"
    greeted = True

    # 대화 기록 텍스트 생성
    history_text = ""
    for i, (q, a) in enumerate(conversation_history[-6:]):
        history_text += f"[대화{i+1}]\n사용자: {q}\nAI: {a}\n"

    # 프롬프트 구성
    prompt = f"""
            당신은 아파트 하자 점검 전문가 AI 챗봇입니다.

            이전 대화 기록:
            {history_text}

            지침:
            - 인삿말은 챗봇이 출력하지 마세요. 첫 인사는 시스템이 이미 출력했습니다.
            - 본론만 정확하고 친절하게 대답해 주세요.
            - 관련 없는 질문은 일반적인 AI 지식으로 간단하고 친절하게 설명하세요.
            - 동일 문장을 반복하지 말고, 줄바꿈과 존댓말을 사용하세요.
            - 같은 내용을 반복하지 말고, 표현을 다양하게 바꿔서 설명하세요.
            - 능숙하다는 표현 대신 어떤 활동에서 사용했는지도 언급하세요.
            사용자 질문: {question}
            """
    print("🧪 사용자 질문:", question)

    try:
        response = llm_model.generate_content([prompt])
        answer = response.text.strip()

        # 대화 기록 저장
        conversation_history.append((question, answer))

        return greeting + answer
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"