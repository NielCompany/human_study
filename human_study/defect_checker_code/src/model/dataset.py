# Dataset 클래스 정의

import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

class DefectDataset(Dataset):
    """
    이미지와 캡션(csv)을 입력 받아 PyTorch 모델 학습용 데이터셋으로 변환
    """

    def __init__(self, csv_path, image_dir, tokenizer, transform=None):
        """
        csv_path: image, caption 이 있는 CSV 파일 경로
        image_dir: 이미지가 저장된 폴더 경로
        tokenizer: 문자열 → 토큰 리스트로 변환하는 클래스
        transform: 이미지 전처리용 transform (없으면 ToTensor 기본 사용)
        """
        self.df = pd.read_csv(csv_path)  # CSV 파일 로드
        self.image_dir = image_dir       # 이미지 폴더 경로 저장
        self.tokenizer = tokenizer       # 주입받은 토크나이저
        self.transform = transform if transform else transforms.ToTensor()  # 기본 이미지 전처리

    def __len__(self):
        """
        전체 샘플 수 반환
        """
        return len(self.df)

    def __getitem__(self, idx):
        """
        index에 해당하는 이미지와 토큰화된 캡션 반환
        """
        row = self.df.iloc[idx]

        # 이미지 경로 만들기
        image_path = os.path.join(self.image_dir, row["image"])

        # 이미지 로드 및 RGB 변환
        image = Image.open(image_path).convert("RGB")

        # 캡션 텍스트
        caption = row["caption"]

        # 이미지 전처리 (Tensor로 변환)
        image = self.transform(image)

        # 캡션을 토큰 리스트로 변환
        caption_tokens = self.tokenizer.encode(caption)

        return image, caption_tokens
