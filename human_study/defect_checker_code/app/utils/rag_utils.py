# 📁 app/utils/rag_utils.py

import os
import pickle
import re
import warnings
import threading
from dotenv import load_dotenv
from .gemini_utils import ask_gemini
import google.generativeai as genai

# suppress TensorFlow and other logs
os.environ.setdefault('TF_ENABLE_ONEDNN_OPTS', '0')
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# 1. ENV 로드 & Gemini API 키 설정
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 2. 전역 캐시 변수 선언
VECTORSTORE_PATH = os.path.join(
    os.path.dirname(__file__),
    'faiss_db',
    'vectorstore.pkl'
)
_vectorstore = None
_llm = None
conversation_history = []

# 3. Vectorstore 동기 로드 
def get_vectorstore():
    """필요 시점에 단 한 번만 pickle 로드"""
    global _vectorstore
    if _vectorstore is None:
        try:
            with open(VECTORSTORE_PATH, 'rb') as f:
                _vectorstore = pickle.load(f)
                print("✅ vectorstore 동기 로드 성공")
        except Exception as e:
            print("❌ vectorstore 로드 실패:", e)
            _vectorstore = None
    return _vectorstore

# 4. LLM 세션 로드
def get_llm():
    global _llm
    if _llm is None:
        try:
            _llm = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ LLM 세션 로드 성공")
        except Exception as e:
            print("❌ LLM 초기화 실패:", e)
            _llm = None
    return _llm

# 1️⃣ 서버 시작 시 미리 로드하기 위한 warmup
def _warmup():
    """백그라운드에서 Vectorstore와 LLM을 미리 로드합니다."""
    try:
        _ = get_vectorstore()
        _ = get_llm()
        print("✅ Warmup complete: vectorstore & LLM ready")
    except Exception as e:
        print("❌ Warmup failed:", e)

# 데몬 스레드로 앱 시작과 동시에 warmup 실행
threading.Thread(target=_warmup, daemon=True).start()

# 5. 응답 정리 함수 (unchanged)
def format_answer(answer: str) -> str:
    answer = re.sub(r"(안녕하세요[.!]?\s*궁금한 내용을 물어보세요!?)", "", answer).strip()
    answer = re.sub(r"\*\*(.*?)\*\*", r"\1", answer)
    answer = re.sub(r"(\d+)\.(\S)", r"\1. \2", answer)
    answer = re.sub(r"\n?[\-\*]{1,2} ?([^\n]+)", r"\n  - \1", answer)
    answer = re.sub(r"\n{3,}", "\n\n", answer)
    answer = re.sub(r"\n[ \t]+", "\n", answer)
    answer = re.sub(r"^AI:\s*", "", answer)
    return answer.strip()

# 6. 메인 RAG 함수 (unchanged)
def answer_with_rag(query: str, top_k: int = 3) -> str:
    global conversation_history

    vectorstore = get_vectorstore()
    print("vectorstore loaded:", bool(vectorstore))
    if not vectorstore:
        return ask_gemini(query)

    docs = vectorstore.similarity_search(query, k=top_k)
    if not docs or all(len(doc.page_content.strip()) < 30 for doc in docs):
        return ask_gemini(query)

    context = '\n\n'.join(doc.page_content for doc in docs)
    history_text = ''.join(
        f"[대화{i+1}]\n사용자: {q}\nAI: {a}\n"
        for i, (q, a) in enumerate(conversation_history[-6:])
    )

    prompt = f"""
    당신은 아파트 하자 점검 AI 비서입니다.
    아래 문서와 대화 기록을 참고하여 사용자 질문에 근거 있는 답변을 제공하세요.

    [문서 요약]
    {context}

    [이전 대화 기록]
    {history_text}

    [질문]
    {query}

    [지침]
    - 친절하고 간결하게 서술
    - 줄바꿈과 들여쓰기로 가독성을 높이세요
    - 문서나 시스템에 정보가 부족하더라도, 유사한 사례나 일반적인 지식에 기반해 정중하고 유용하게 답변하세요.
    - "해당 기능을 제공하지 않습니다" 또는 "답변할 수 없습니다", 현재 제공된 문서에서 찾을 수 없습니다. 와 같은 부정적인 표현은 피하세요.
    - 인삿말은 챗봇이 출력하지 마세요. 첫 인사는 시스템이 이미 출력했습니다.
    - 동일 문장을 반복하지 말고, 줄바꿈과 존댓말을 사용하세요.
    - 같은 내용을 반복하지 말고, 표현을 다양하게 바꿔서 설명하세요.
    - 능숙하다는 표현 대신 어떤 활동에서 사용했는지도 언급하세요.
    - 항목 나열 시 숫자나 하이픈(-), 들여쓰기, 줄바꿈을 명확하게 사용하여 가독성을 높이세요.
    - 마크다운 대신 일반 텍스트 방식으로 포맷팅하세요. 예: "1. 항목", " - 세부사항", 빈 줄 사용
    """

    try:
        llm = get_llm()
        response = llm.generate_content(prompt)
        answer = format_answer(response.text.strip())
        conversation_history.append((query, answer))
        return answer
    except Exception as e:
        return f"❌ 오류 발생: {e}"
