# # CNN + LSTM 모델 정의

# import torch
# import torch.nn as nn
# import torchvision.models as models

# class EncoderCNN(nn.Module):
#     """
#     이미지 특징 추출기 (사전학습된 ResNet50 사용)
#     """
#     def __init__(self, embed_size):
#         super(EncoderCNN, self).__init__()
#         resnet = models.resnet50(pretrained=True)
#         modules = list(resnet.children())[:-1]  # 마지막 FC layer 제거
#         self.resnet = nn.Sequential(*modules)
#         self.linear = nn.Linear(resnet.fc.in_features, embed_size)
#         self.bn = nn.BatchNorm1d(embed_size)

#     def forward(self, images):
#         with torch.no_grad():
#             features = self.resnet(images)  # (B, 2048, 1, 1)
#         features = features.view(features.size(0), -1)  # (B, 2048)
#         features = self.bn(self.linear(features))       # (B, embed_size)
#         return features


# class DecoderRNN(nn.Module):
#     """
#     캡션 생성기 (LSTM 기반)
#     """
#     def __init__(self, embed_size, hidden_size, vocab_size, num_layers=1):
#         super(DecoderRNN, self).__init__()
#         self.embed = nn.Embedding(vocab_size, embed_size)
#         self.lstm = nn.LSTM(embed_size, hidden_size, num_layers, batch_first=True)
#         self.linear = nn.Linear(hidden_size, vocab_size)

#     def forward(self, features, captions):
#         """
#         features: (B, embed_size)
#         captions: (B, seq_len)
#         """
#         embeddings = self.embed(captions)               # (B, seq_len, embed_size)
#         inputs = torch.cat((features.unsqueeze(1), embeddings), 1)  # 앞에 이미지 feature 추가
#         hiddens, _ = self.lstm(inputs)                  # (B, seq_len+1, hidden_size)
#         outputs = self.linear(hiddens)                  # (B, seq_len+1, vocab_size)
#         return outputs

# model_train.py

from image_resize_2 import get_dataloaders
import torchvision.models as models
import torch.nn as nn

train_loader, val_loader, train_dataset = get_dataloaders()
num_classes = len(train_dataset.classes)

model = models.resnet34(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, num_classes)
