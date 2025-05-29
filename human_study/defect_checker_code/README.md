# 하자 점검 AI 프로젝트

File Tree

defect_checker/                          # 최상위 프로젝트 폴더
├── data/                                # 원본 이미지, OCR 결과 등 저장
│   ├── raw/                             # 원본 이미지들 (스캔된 하자 사진 등)
│   ├── processed/                       # 전처리된 이미지들 (크롭, 리사이즈 등)
│   ├── ocr_texts/                       # OCR 추출 텍스트 (json or csv)
│   └── samples/                         # 테스트 샘플 이미지 (개발용)
│       └── test.jpg
│
├── dataset/                             # 학습용 데이터셋 구성 파일
│   ├── annotations.csv                  # 이미지-설명 매칭 정보
│   ├── train/                           # 학습용 이미지 복사본
│   ├── val/                             # 검증용 이미지 복사본
│   └── test/                            # 테스트용 이미지 복사본
│
├── models/                              # 저장된 모델 체크포인트
│   └── baseline_caption_model.pth
│
├── src/                                 # 주요 파이썬 코드
│   ├── ocr/
│   │   └── run_ocr.py                   # easyocr로 텍스트 추출 코드
│   ├── preprocess/
│   │   └── image_cleaner.py            # 이미지 전처리 관련 함수
│   ├── training/
│   │   └── train_captioning.py         # 이미지 캡셔닝 모델 학습 코드
│   ├── inference/
│   │   └── run_inference.py            # 모델 추론 (이미지 → 설명)
│   └── utils/
│       └── helpers.py                  # 공통 유틸 함수
│   └── model/
│       ├── dataset.py         # Dataset 클래스 정의
│       ├── tokenizer.py       # 단어 → 숫자 매핑용 토크나이저
│       ├── model.py           # CNN + LSTM 모델 정의
│       ├── train.py           # 학습 루프
│       └── predict.py         # 추론 (예측 결과 확인)
│
├── tests/                               # 테스트 코드 모음
│   └── test_ocr_pipeline.py
│
├── app/                                 # 추후 웹 앱 또는 API 구성
│   ├── main.py                          # Streamlit or Flask 진입점
│   └── templates/                       # HTML 템플릿 등
│
├── logs/                                # 학습/실행 로그
│   └── train_log.txt
│
├── requirements.txt                    # 의존성 목록
├── README.md                           # 프로젝트 설명
└── config.yaml                         # 하이퍼파라미터, 경로 등 설정파일