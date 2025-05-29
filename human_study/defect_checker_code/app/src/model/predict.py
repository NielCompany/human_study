# src/model/predict.py
import torch
from torchvision import transforms, models, datasets
from PIL import Image
import os

# # ✅ 클래스 정보 (ImageFolder 기준)
# train_dataset = datasets.ImageFolder('./dataset/train')
# classes = train_dataset.classes

classes = [
    "개폐 불량","고정 불량","균열","누수","도배 불량","도장 불량","랩핑 불량","마감 불량","마루 불량",
    "문틀 불량","벽체 불량","수직 및 수평 불량","수직 수평 불량","수평 불량","시공 불량",
    "시공 확인 필요","없음","오염","자재 불량","줄눈 마감 불량","코킹 불량","타공 불량","타일 불량"
]

# ✅ 모델 준비
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet50(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, len(classes))
model.load_state_dict(torch.load('models/resnet50_yolov5_acc.pth', map_location=device))
model = model.to(device)
model.eval()

# ✅ 전처리 정의
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

# ✅ 예측 함수 (이미지 경로 받아서 클래스 반환)
def predict_image(image_path):
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(image)
        pred_idx = torch.argmax(outputs, 1).item()
        pred_class = classes[pred_idx]

    return pred_class
