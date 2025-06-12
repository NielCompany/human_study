# # app/utils/build_vectorstore.py

# import os
# import pickle
# from langchain.vectorstores import FAISS
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.schema import Document

# # 1. 텍스트 로드
# file_path = os.path.join(os.path.dirname(__file__), "defect_knowledge.txt")
# with open(file_path, "r", encoding="utf-8") as f:
#     raw_text = f.read()

# # 2. 문단 단위로 나누기
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# texts = text_splitter.create_documents([raw_text])

# # 3. 임베딩 모델 로드
# embedding_model = HuggingFaceEmbeddings(model_name="jhgan/ko-sbert-nli")

# # 4. FAISS 벡터스토어 생성
# vectorstore = FAISS.from_documents(texts, embedding_model)

# # 5. 저장
# save_path = os.path.join(os.path.dirname(__file__), "faiss_db")
# vectorstore.save_local(save_path)

# # ✅ 캐시도 저장 (추후 빠른 로드용)
# with open(os.path.join(save_path, "vectorstore.pkl"), "wb") as f:
#     pickle.dump(vectorstore, f)

# print("✅ FAISS 벡터스토어 생성 완료!")
