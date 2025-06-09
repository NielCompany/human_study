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
import re

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
greeted = True
conversation_history = []

# 응답 정리 함수 추가 
def format_answer(answer: str) -> str:
    # 1. 불필요한 인삿말 제거
    answer = re.sub(r"(안녕하세요[.!]?\s*궁금한 내용을 물어보세요!?)*", "", answer).strip()

    # 2. 마크다운 강조 제거 (**내용** → 내용)
    answer = re.sub(r"\*\*(.*?)\*\*", r"\1", answer)

    # 3. 번호와 내용 사이 띄어쓰기 추가 (1.내용 → 1. 내용)
    answer = re.sub(r"(\d+)\.(\S)", r"\1. \2", answer)

    # 4. 하이픈(-), 별표(*)로 시작하는 항목 정리 → 들여쓰기
    answer = re.sub(r"\n?[\-\*]{1,2} ?([^\n]+)", r"\n  - \1", answer)

    # 5. 여러 줄 바꿈 정리 (3줄 이상 → 2줄)
    answer = re.sub(r"\n{3,}", "\n\n", answer)

    # 6. 줄 바꿈 후 공백 제거
    answer = re.sub(r"\n[ \t]+", "\n", answer)

    # 7. "AI:" 제거 (불필요한 접두사일 경우)
    answer = re.sub(r"^AI:\s*", "", answer)

    return answer.strip()



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
            - 문서나 시스템에 정보가 부족하더라도, 유사한 사례나 일반적인 지식에 기반해 정중하고 유용하게 답변하세요.
            - "해당 기능을 제공하지 않습니다" 또는 "답변할 수 없습니다"와 같은 부정적인 표현은 피하세요.
            - 동일 문장을 반복하지 말고, 줄바꿈과 존댓말을 사용하세요.
            - 같은 내용을 반복하지 말고, 표현을 다양하게 바꿔서 설명하세요.
            - 능숙하다는 표현 대신 어떤 활동에서 사용했는지도 언급하세요.
            - 항목 나열 시 **숫자나 하이픈(-), 들여쓰기, 줄바꿈을 명확하게 사용하여 가독성을 높이세요.**
            - 마크다운 대신 일반 텍스트 방식으로 포맷팅하세요. 예: "1. 항목", " - 세부사항", 빈 줄 사용
            사용자 질문: {question}
            """
    print("🧪 사용자 질문:", question)

    try:
        response = llm_model.generate_content([prompt])
        answer = response.text.strip()
        answer = format_answer(answer)  # ✅ 응답 정리 함수 적용

        # 대화 기록 저장
        conversation_history.append((question, answer))

        if greeting:
            return greeting  # 첫 호출일 경우 인사만 출력하고 끝
        else:
            return answer  # 이후 호출은 본론만 출력
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"