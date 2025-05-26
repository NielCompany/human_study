import pandas as pd
import os
import shutil
from sklearn.model_selection import train_test_split

# 1. 경로 설정
csv_path = './dataset/processed_image_class.csv'
img_dir = './dataset/sum_images/'  # image16580.jpg 등이 있는 폴더
train_dir = './dataset/train/'
val_dir = './dataset/val/'

# 2. 데이터 불러오기
df = pd.read_csv(csv_path)

# 3. 클래스 폴더 만들기
os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)

# 4. train/val split (stratify는 클래스 비율 유지)
train_df, val_df = train_test_split(df, test_size=0.2, stratify=df['class'], random_state=42)

# 5. 파일 복사 함수
def copy_files(split_df, split_dir):
    for _, row in split_df.iterrows():
        cls_folder = os.path.join(split_dir, row['class'])
        os.makedirs(cls_folder, exist_ok=True)
        src = os.path.join(img_dir, row['image'])
        dst = os.path.join(cls_folder, row['image'])
        shutil.copyfile(src, dst)

copy_files(train_df, train_dir)
copy_files(val_df, val_dir)
