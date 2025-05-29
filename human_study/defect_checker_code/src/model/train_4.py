# # 학습 루프

# import os
# import torch
# from torch.utils.data import DataLoader
# from torch import nn, optim
# from src.model.dataset import DefectDataset
# from src.model.tokenizer import MyTokenizer
# from src.model.model import EncoderCNN, DecoderRNN
# from torchvision import transforms
# from torch.nn.utils.rnn import pad_sequence
# from tqdm import tqdm

# # ✅ 하이퍼파라미터 설정
# csv_path = "data/train_caption.csv"
# image_dir = "data/samples"
# batch_size = 32
# embed_size = 256
# hidden_size = 512
# num_epochs = 10
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# # ✅ 이미지 전처리 (ResNet 입력 크기 맞춤)
# transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor()
# ])

# # ✅ 토크나이저 & 데이터셋
# tokenizer = MyTokenizer(csv_path)
# dataset = DefectDataset(csv_path, image_dir, tokenizer, transform)
# vocab_size = tokenizer.vocab_size()

# # ✅ DataLoader 정의 (캡션은 패딩 필요)
# def collate_fn(batch):
#     images, captions = zip(*batch)
#     images = torch.stack(images)

#     # 캡션 길이 다르므로 패딩
#     captions = [torch.tensor(cap) for cap in captions]
#     captions_padded = pad_sequence(captions, batch_first=True, padding_value=0)

#     return images, captions_padded

# dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)

# # ✅ 모델 구성
# encoder = EncoderCNN(embed_size).to(device)
# decoder = DecoderRNN(embed_size, hidden_size, vocab_size).to(device)

# # ✅ 손실 함수 & 옵티마이저
# criterion = nn.CrossEntropyLoss(ignore_index=0)  # <PAD> 무시
# params = list(decoder.parameters()) + list(encoder.linear.parameters()) + list(encoder.bn.parameters())
# optimizer = optim.Adam(params, lr=1e-3)

# # ✅ 학습 루프
# for epoch in range(num_epochs):
#     encoder.train()
#     decoder.train()
#     epoch_loss = 0

#     for images, captions in tqdm(dataloader, desc=f"Epoch {epoch+1}/{num_epochs}"):
#         images, captions = images.to(device), captions.to(device)

#         # 입력: caption의 앞부분 / 타겟: caption의 뒷부분
#         inputs = captions[:, :-1]
#         targets = captions[:, 1:]

#         features = encoder(images)
#         outputs = decoder(features, inputs)

#         # outputs: (B, seq_len, vocab) → (B*seq_len, vocab)
#         outputs = outputs[:, 1:, :]  # decoder의 출력이 1개 더 길기 때문에 자름

#         # 손실 계산
#         loss = criterion(outputs.reshape(-1, vocab_size), targets.reshape(-1))

#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()

#         epoch_loss += loss.item()

#     avg_loss = epoch_loss / len(dataloader)
#     print(f"✅ Epoch {epoch+1} 평균 손실: {avg_loss:.4f}")

# # ✅ 모델 저장
# torch.save({
#     'encoder_state_dict': encoder.state_dict(),
#     'decoder_state_dict': decoder.state_dict(),
#     'tokenizer': tokenizer.word2idx
# }, "model_caption.pth")

# print("🎉 학습 완료 및 모델 저장됨: model_caption.pth")

import torch
from sklearn.metrics import f1_score, accuracy_score
import numpy as np
from model_3 import model
import torch.nn as nn
from image_resize_2 import get_dataloaders

train_loader, val_loader, train_dataset = get_dataloaders()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

from tqdm import tqdm
import time

best_f1 = 0
total_epochs = 10

for epoch in range(total_epochs):
    start_time = time.time()
    model.train()
    train_loss = 0.0
    train_loop = tqdm(train_loader, desc=f"[Epoch {epoch+1}/{total_epochs}] Training", leave=False)

    for imgs, labels in train_loop:
        imgs, labels = imgs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        train_loop.set_postfix(loss=loss.item())

    # 검증
    model.eval()
    val_preds, val_trues = [], []
    val_loop = tqdm(val_loader, desc=f"[Epoch {epoch+1}/{total_epochs}] Validating", leave=False)

    with torch.no_grad():
        for imgs, labels in val_loop:
            imgs = imgs.to(device)
            outputs = model(imgs)
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            val_preds.extend(preds)
            val_trues.extend(labels.numpy())

    acc = accuracy_score(val_trues, val_preds)
    f1 = f1_score(val_trues, val_preds, average='macro')

    elapsed = time.time() - start_time
    print(f"📘 Epoch {epoch+1} | Loss: {train_loss:.4f} | Acc: {acc:.4f} | F1: {f1:.4f} | ⏱️ Time: {elapsed:.2f}s")

    if f1 > best_f1:
        best_f1 = f1
        torch.save(model.state_dict(), 'best_model.pth')
        print("✅ Best model saved (F1:", round(best_f1, 4), ")")