# 📁 app/utils/rag_utils.py
import os
import pickle
import re
import warnings
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document
import google.generativeai as genai
from .gemini_utils import ask_gemini

# suppress TensorFlow and other logs
os.environ.setdefault('TF_ENABLE_ONEDNN_OPTS', '0')
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '2')
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# 1. ENV 로드 and genai configure at module load
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# 2. 전역 캐시 변수 선언
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), 'faiss_db', 'vectorstore.pkl')
_vectorstore = None
_llm = None
_embedding_model = None
conversation_history = []

# 3. Lazy 초기화 함수

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None and os.path.exists(VECTORSTORE_PATH):
        with open(VECTORSTORE_PATH, 'rb') as f:
            _vectorstore = pickle.load(f)
    return _vectorstore


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(model_name='jhgan/ko-sbert-nli')
    return _embedding_model


def get_llm():
    global _llm
    if _llm is None:
        # genai already configured at import, just instantiate
        _llm = genai.GenerativeModel('gemini-2.0-flash')
    return _llm

# 4. 응답 정리 함수 (unchanged)

def format_answer(answer: str) -> str:
    answer = re.sub(r"(안녕하세요[.!]?\s*궁금한 내용을 물어보세요!?)", "", answer).strip()
    answer = re.sub(r"\*\*(.*?)\*\*", r"\1", answer)
    answer = re.sub(r"(\d+)\.(\S)", r"\1. \2", answer)
    answer = re.sub(r"\n?[\-\*]{1,2} ?([^\n]+)", r"\n  - \1", answer)
    answer = re.sub(r"\n{3,}", "\n\n", answer)
    answer = re.sub(r"\n[ \t]+", "\n", answer)
    answer = re.sub(r"^AI:\s*", "", answer)
    return answer.strip()

# 5. 메인 RAG 함수 (lazy init 적용)

def answer_with_rag(query: str, top_k: int = 3) -> str:
    global conversation_history

    vectorstore = get_vectorstore()
    if not vectorstore:
        return ask_gemini(query)

    docs: list[Document] = vectorstore.similarity_search(query, k=top_k)
    if not docs or all(len(doc.page_content.strip()) < 30 for doc in docs):
        return ask_gemini(query)

    context = '\n\n'.join(doc.page_content for doc in docs)
    history_text = ''.join(
        f"[대화{i+1}]\n사용자: {q}\nAI: {a}\n" for i, (q, a) in enumerate(conversation_history[-6:])
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