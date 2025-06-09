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

mapping_data = """
            도배 불량 : 도배 마감 불량, 도배 주름짐, 도배 면 불량, 도배 조인트 불량, 도배 태움 불량, 도배 오염, 도배 들뜸, 도배 요철, 도배 찢김
            타일 불량 : 타일 채움 불량, 타일 오염, 타일 들뜸, 타일 손상, 타일 구배 불량, 타일 오타공, 타일 줄눈 마감 불량
            마루 불량 : 마루 들뜸, 마루 수평 불량, 마루 틈새, 마루 단차
            코킹 불량 : 코킹 마감 불량, 코킹 오염, 코킹 미시공
            자재 불량 : 자재 오염, 자재 불량, 자재 손상, 자재 미시공, 자재 고정 불량, 수평 불량, 수직 불량, 수평 수직 불량, 자재 틈새, 자재 맞춤 불량, 자재 재단 불량, 자재 도장 오염, 자재 오타공, 자재 단차, 자재 줄눈 마감 불량, 자재 조인트 불량, 자재 단차, 씰 손상
            랩핑 불량 : 랩핑 들뜸, 랩핑 손상, 랩핑 오염
            문틀 불량 : 문틀 오염, 문틀 고정 불량, 문틀 도장 불량, 문틀 도장 오염, 문틀 틀어짐
            창틀 불량 : 창틀 흔들림, 창틀 틈새, 창틀 오염, 창틀 도장 오염
            벽면 불량 : 벽면 도장 불량
            벽체 불량 : 벽체 오타공, 벽체 틀어짐, 벽체 고정 불량, 평활도 불량
            창호 불량 : 창호 오타공
            천장 불량 : 천장 오타공, 천장 시공 불량, 천장 마감 불량
            수직 및 수평 불량 : 수직 불량, 수평 불량, 수직 수평 불량, 레벨 확인 필요
            타공 불량 : 타공 마감 불량, 오타공, 타공 마감 누락
            줄눈 마감 불량
            시공 불량 : 시공 불량 - 틈새, 시공 불량 - 유격, 시공 불량 - 개폐 불량, 시공 불량 - 수평, 시공 불량 - 수직, 시공 불량 - 수직 및 수평, 시공 불량 - 수평 및 수직, 시공 불량 - 면처리 불량, 시공 불량 - 도장 불량, 시공 마감 요망, 시공 불량 - 평활도 불량, 시공 불량 - 구배 불량, 시공 불량 - 줄눈 불량, 시공 불량 - 줄눈 누락, 시공 불량 - 채움 불량, 시공 불량 - 사춤 불량, 시공 불량 - 창틀 흔들림
            시공 확인 필요
            마감 불량 : 마감 누락, 마감 불량, 마감 요망
            개폐 불량
            균열
            누수
            사춤 불량
            """


# ✅ 모델 준비
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.resnet50(weights=None)
model.fc = torch.nn.Linear(model.fc.in_features, len(classes))
model.load_state_dict(torch.load('models/label_labeled_sum_acc.pth', map_location=device))
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

# ✅ string → dict로 변환
def parse_mapping_data(mapping_text):
    mapping_dict = {}
    for line in mapping_text.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value_list = [v.strip() for v in value.split(",")]
            mapping_dict[key] = value_list
        else:
            key = line.strip()
            mapping_dict[key] = []
    return mapping_dict

# ✅ dict로 변환
mapping_dict = parse_mapping_data(mapping_data)

def get_defect_keywords(predicted_class):
    return mapping_dict.get(predicted_class, [])


# # ✅ 예측된 대분류 클래스 기반으로 세부 하자 항목 리스트 반환
# def get_defect_keywords(predicted_class):
#     return mapping_data.get(predicted_class, [])