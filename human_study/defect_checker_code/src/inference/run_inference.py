# 모델 추론 코드

# 학습된 모델로 이미지 → 설명 생성
def run_inference(image_path, model_path):
    print(f"📸 {image_path} 에 대해 추론 시작")
    # TODO: 모델 로딩, 이미지 처리, 결과 출력

if __name__ == "__main__":
    run_inference("dataset/test/sample.jpg", "models/baseline_caption_model.pth")