# from model_3 import model
from image_resize_2 import get_dataloaders
from torchvision import transforms, models, datasets
# from intergration_training import model
import torch
from PIL import Image
import os
import csv
from tqdm import tqdm

# ✅ 클래스 자동 로딩
train_dataset = datasets.ImageFolder('./dataset/train')
classes = train_dataset.classes  # ← 순서 보장됨

# ✅ 모델 정의
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet50(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, len(classes))
model.load_state_dict(torch.load('best_resnet50.pth', map_location=device))
model = model.to(device)
model.eval()

# ✅ 전처리
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
])

# ✅ 폴더 순회 예측
input_folder = './dataset/test'
output_csv = 'test_predictions2.csv'
results = []

for img_name in tqdm(os.listdir(input_folder)):
    if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(input_folder, img_name)
        image = Image.open(img_path).convert('RGB')
        image = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(image)
            pred_idx = torch.argmax(outputs, 1).item()
            pred_class = classes[pred_idx]

        results.append([img_name, pred_class])

# ✅ CSV 저장
with open(output_csv, mode='w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['image_name', 'predicted_class'])
    writer.writerows(results)

print("✅ 예측 완료 →", output_csv)