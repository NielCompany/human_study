import pandas as pd
import os
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from imblearn.over_sampling import RandomOverSampler
from sklearn.preprocessing import LabelEncoder

# ✅ 커스텀 Dataset 정의
class CSVDataset(Dataset):
    def __init__(self, dataframe, img_dir, transform=None):
        self.data = dataframe
        self.img_dir = img_dir
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        img_path = os.path.join(self.img_dir, row['image'])
        image = Image.open(img_path).convert('RGB')
        label = row['label']
        if self.transform:
            image = self.transform(image)
        return image, label

# ✅ CSV 불러오기 및 레이블 인코딩
df = pd.read_csv('./dataset/processed_image_class.csv')  # image, class 컬럼
le = LabelEncoder()
df['label'] = le.fit_transform(df['class'])

# ✅ Oversampling 적용
ros = RandomOverSampler()
X_resampled, y_resampled = ros.fit_resample(df[['image']], df['label'])

# ✅ Oversampled DataFrame 구성
df_resampled = pd.DataFrame({
    'image': X_resampled['image'],
    'label': y_resampled
})
df_resampled['class'] = le.inverse_transform(df_resampled['label'])

# ✅ 전처리 정의
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

# ✅ Dataset & DataLoader 생성
train_dataset = CSVDataset(df_resampled, img_dir='./dataset/train', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
