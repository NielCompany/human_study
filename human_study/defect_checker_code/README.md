## 하자 점검 AI 프로젝트

# Defect Checker AI 시스템

현장 사진에서 자동으로 하자(결함) 정보를 추출하고, 텍스트로 설명을 생성하는 종단 간(A→Z) 인공지능 파이프라인입니다. OCR, 이미지 전처리, 캡셔닝 모델 학습과 추론, 그리고 테스트·배포 준비까지 모두 포함하고 있습니다.

---

 주요 기능

- OCR 텍스트 추출  
  스캔된 하자 사진에서 EasyOCR을 이용해 텍스트를 자동으로 추출합니다.  
- 이미지 전처리  
  크롭, 리사이즈, 노이즈 제거 등 모델 학습과 추론에 최적화된 형태로 이미지를 정리합니다.  
- 이미지 캡셔닝 모델  
  CNN과 LSTM 기반의 네트워크로 이미지 안의 하자 상황을 자연어 설명으로 생성합니다.  
- 추론 워크플로우  
  학습된 모델을 활용해 새로운 사진에서 자동으로 하자 설명을 출력합니다.  
- 유닛 테스트  
  핵심 OCR 파이프라인과 주요 유틸 함수에 대해 자동화된 테스트를 제공합니다.  
- 웹 앱/API (예정)  
  Streamlit 또는 Flask로 간단한 UI/API를 구성하고, 현장 담당자가 바로 사용해 볼 수 있게 준비 중입니다.

---
- defect_checker/
  - data/
    - raw/                 # 원본 이미지들 (스캔된 하자 사진 등)
    - processed/          # 전처리된 이미지들 (크롭, 리사이즈 등)
    - ocr_texts/          # OCR 추출 텍스트 (JSON or CSV)
    - samples/            # 테스트 샘플 이미지
      - test.jpg
  - dataset/
    - annotations.csv     # 이미지-설명 매칭 정보
    - train/              # 학습용 이미지
    - val/                # 검증용 이미지
    - test/               # 테스트용 이미지
  - models/
    - baseline_caption_model.pth # 저장된 모델 체크포인트
  - src/
    - ocr/
      - run_ocr.py        # EasyOCR로 텍스트 추출
    - preprocess/
      - image_cleaner.py  # 이미지 전처리 함수
    - training/
      - train_captioning.py # 이미지 캡셔닝 모델 학습
    - inference/
      - run_inference.py  # 모델 추론 (이미지 → 설명)
    - utils/
      - helpers.py        # 공통 유틸 함수
    - model/
      - dataset.py        # `Dataset` 클래스 정의
      - tokenizer.py      # 단어 ↔ 토큰 매핑
      - model.py          # CNN + LSTM 모델 정의
      - train.py          # 학습 루프
      - predict.py        # 추론 스크립트
  - tests/
    - test_ocr_pipeline.py # OCR 파이프라인 유닛 테스트
  - app/
    - main.py             # Streamlit/Flask 진입점
    - templates/          # HTML 템플릿 등
  - logs/
    - train_log.txt       # 학습 및 실행 로그
  - requirements.txt      # Python 의존성 목록
  - config.yaml          # 하이퍼파라미터 및 경로 설정
  - README.md            # 프로젝트 설명

---

 설치 및 실행 요약

1. 저장소를 클론하고 가상환경을 생성합니다.  
2. `requirements.txt`를 통해 필요한 패키지를 설치합니다.  
3. `config.yaml`에서 데이터 경로와 학습 파라미터를 설정합니다.  
4. 순서대로 OCR → 이미지 전처리 → 데이터셋 준비 → 모델 학습 → 추론 파이프라인을 실행합니다.  
5. `pytest` 명령으로 테스트를 수행해 안정성을 확인합니다.

---

 설정 파일 개요 (`config.yaml`)

- data  
  - 원본·전처리 이미지 폴더와 OCR 결과, 어노테이션 파일 경로  
- model  
  - 임베딩 크기, LSTM 히든 크기, 레이어 수 등 모델 구조  
- training  
  - 배치 크기, 에폭 수, 학습률 등 학습 관련 파라미터  
- inference  
  - 빔 서치 크기 등 추론 옵션

---

 향후 계획

- 웹 인터페이스 배포  
  현장 담당자가 손쉽게 업로드·결과 확인 가능한 Flask 앱 완성  
- 사용자 피드백 기반 지속 학습  
  모델 예측 결과를 검수 후 재학습하여 성능 향상  
- 모니터링 대시보드  
  OCR 신뢰도, 모델 정확도, 로그 현황을 시각화  
- 클라우드 배포  
  AWS/GCP 기반 자동 확장 추론 서비스 구축

---

 라이선스

이 프로젝트는 MIT License 하에 배포됩니다.  
