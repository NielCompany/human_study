# src/model/predict.py
import torch
from torchvision import transforms, models, datasets
from PIL import Image
import os

# ✅ 클래스 정보 (ImageFolder 기준)
train_dataset = datasets.ImageFolder('./dataset/train')
classes = train_dataset.classes

# ✅ 모델 준비
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet50(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, len(classes))
model.load_state_dict(torch.load('best_resnet50.pth', map_location=device))
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
