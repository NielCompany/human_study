import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import RandomOverSampler

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from tqdm import tqdm

# ✅ 1. 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Using device: {device}")

# ✅ 2. CSV 불러오기 및 라벨 인코딩
df = pd.read_csv('./dataset/processed_image_class.csv')  # image, class 컬럼
le = LabelEncoder()
df['label'] = le.fit_transform(df['class'])

# ✅ 3. train/val 분리
train_df, val_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)

# ✅ 4. Oversampling 학습셋만 적용
ros = RandomOverSampler()
X_res, y_res = ros.fit_resample(train_df[['image']], train_df['label'])
train_df_resampled = pd.DataFrame({'image': X_res['image'], 'label': y_res})
train_df_resampled['class'] = le.inverse_transform(train_df_resampled['label'])

# ✅ 5. 이미지 전처리 정의
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

# ✅ 6. 커스텀 Dataset
class CSVDataset(Dataset):
    def __init__(self, dataframe, img_dir, transform=None):
        self.data = dataframe.reset_index(drop=True)
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

# ✅ 7. DataLoader 설정
img_dir = './dataset/sum_images'
batch_size = 32

train_dataset = CSVDataset(train_df_resampled, img_dir, transform=transform)
val_dataset = CSVDataset(val_df, img_dir, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
num_classes = len(le.classes_)

# ✅ 8. 모델 정의
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, num_classes)
model = model.to(device)

# ✅ 9. 손실함수 + 옵티마이저
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

# ✅ 10. 학습 루프 설정
num_epochs = 50
early_stopping_patience = 5
best_val_loss = float('inf')
patience_counter = 0
train_losses = []
val_losses = []

# ✅ 11. 학습 루프
for epoch in range(num_epochs):
    start_time = time.time()
    model.train()
    train_loss = 0.0
    train_loop = tqdm(train_loader, desc=f"[Epoch {epoch+1}/{num_epochs}] Training")

    for imgs, labels in train_loop:
        imgs, labels = imgs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        train_loop.set_postfix(loss=loss.item())

    train_loss /= len(train_loader)
    train_losses.append(train_loss)

    # ✅ 검증
    model.eval()
    val_loss = 0.0
    val_preds, val_trues = [], []

    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            val_loss += loss.item()

            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            val_preds.extend(preds)
            val_trues.extend(labels.cpu().numpy())

    val_loss /= len(val_loader)
    val_losses.append(val_loss)

    acc = accuracy_score(val_trues, val_preds)
    f1 = f1_score(val_trues, val_preds, average='macro')
    elapsed = time.time() - start_time

    print(f"\n📘 Epoch {epoch+1} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Acc: {acc:.4f} | F1: {f1:.4f} | ⏱ {elapsed:.2f}s")

    # ✅ 모델 저장 기준: val_loss
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'best_resnet50.pth')
        patience_counter = 0
        print("✅ Best model saved (Val Loss:", round(val_loss, 4), ")")
    else:
        patience_counter += 1
        print(f"⏳ Patience: {patience_counter}/{early_stopping_patience}")
        if patience_counter >= early_stopping_patience:
            print("🛑 Early stopping triggered.")
            break

# ✅ 손실 곡선 시각화
plt.figure(figsize=(10, 5))
plt.plot(train_losses, label='Train Loss')
plt.plot(val_losses, label='Validation Loss')
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Training vs Validation Loss")
plt.legend()
plt.grid(True)
plt.savefig("loss_plot.png")
plt.show()
