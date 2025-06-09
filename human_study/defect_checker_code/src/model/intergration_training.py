import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import f1_score, accuracy_score
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
import time

# ✅ 디바이스 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Using device: {device}")

# ✅ 하이퍼파라미터
batch_size = 32
num_epochs = 50
early_stopping_patience = 5
best_val_loss = float('inf')
patience_counter = 0

# ✅ 전처리 정의 (비율 유지 후 센터 크롭)
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

# ✅ 데이터 로딩
train_dataset = datasets.ImageFolder('./dataset/train', transform=transform)
val_dataset = datasets.ImageFolder('./dataset/val', transform=transform)
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
num_classes = len(train_dataset.classes)

# ✅ 모델 정의
model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
model.fc = nn.Linear(model.fc.in_features, num_classes)
model = model.to(device)

# ✅ 손실함수 + 옵티마이저
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

# ✅ 학습 기록용
train_losses = []
val_losses = []

# ✅ 학습 루프
for epoch in range(num_epochs):
    start_time = time.time()
    model.train()
    train_loss = 0.0
    train_loop = tqdm(train_loader, desc=f"[Epoch {epoch+1}/{num_epochs}] Training", leave=True)

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
        torch.save(model.state_dict(), 'best_resnet50_2.pth')
        patience_counter = 0
        print("✅ Best model saved (Val Loss:", round(val_loss, 4), ")")
    # else:
    #     patience_counter += 1
    #     print(f"⏳ Patience: {patience_counter}/{early_stopping_patience}")
    #     if patience_counter >= early_stopping_patience:
    #         print("🛑 Early stopping triggered.")
    #         break

# ✅ 손실 곡선 그리기
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
