# 📁 app/utils/rag_utils.py
import os
import pickle
import re
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import google.generativeai as genai
from .gemini_utils import ask_gemini



# 1. 환경 변수 및 모델 설정
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
llm = genai.GenerativeModel("gemini-2.0-flash")

# 2. 벡터스토어 경로
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), "faiss_db", "vectorstore.pkl")

# 3. 임베딩 모델
embedding_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli")

# 4. 대화 기록 전역 변수
greeted = False
conversation_history = []

# 5. 응답 정리 함수
def format_answer(answer: str) -> str:
    answer = re.sub(r"(안녕하세요[.!]?\s*궁금한 내용을 물어보세요!?)*", "", answer).strip()
    answer = re.sub(r"\*\*(.*?)\*\*", r"\1", answer)
    answer = re.sub(r"(\d+)\.(\S)", r"\1. \2", answer)
    answer = re.sub(r"\n?[\-\*]{1,2} ?([^\n]+)", r"\n  - \1", answer)
    answer = re.sub(r"\n{3,}", "\n\n", answer)
    answer = re.sub(r"\n[ \t]+", "\n", answer)
    answer = re.sub(r"^AI:\s*", "", answer)
    return answer.strip()

# ✅ 6. 메인 RAG 함수
def answer_with_rag(query: str, top_k=3) -> str:
    global conversation_history

    # 1. 벡터스토어 로드
    if not os.path.exists(VECTORSTORE_PATH):
        return ask_gemini(query)  # fallback to 일반 지식 모드

    with open(VECTORSTORE_PATH, "rb") as f:
        vectorstore = pickle.load(f)

    # 2. 유사한 문서 검색
    docs: list[Document] = vectorstore.similarity_search(query, k=top_k)

    # 2-1. 관련 문서가 거의 없으면 일반 지식으로 fallback
    if not docs or all(len(doc.page_content.strip()) < 30 for doc in docs):
        return ask_gemini(query)  # ✅ 일반 LLM 답변으로 fallback

    # 3. context와 대화 기록 구성
    context = "\n\n".join([doc.page_content for doc in docs])
    history_text = ""
    for i, (q, a) in enumerate(conversation_history[-6:]):
        history_text += f"[대화{i+1}]\n사용자: {q}\nAI: {a}\n"

    # 4. 프롬프트 구성
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
        response = llm.generate_content(prompt)
        answer = format_answer(response.text.strip())
        conversation_history.append((query, answer))
        return answer
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"


