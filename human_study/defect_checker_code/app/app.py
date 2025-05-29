# 추후 웹 앱용 진입점 (Flask or Streamlit)
from flask import Flask, render_template, request
import os
# from werkzeug.utils import secure_filename
# from model.predict import predict_defect_class  # 예측 함수
# from utils.gemini_utils import explain_by_gemini  # Gemini 설명 함수

# upload_bp = Blueprint("upload", __name__)



# app = create_app()
app = Flask(__name__)




## index rendering 
@app.route("/")
def index():
    return render_template("index.html")

# predict----------------------------------------------------------------------------------------

from werkzeug.utils import secure_filename
from src.model.predict import predict_image, get_defect_keywords
from utils.gemini_utils import explain_by_gemini  # Gemini API 호출 함수
import os

#UPLOAD_FOLDER = 'static/uploads'
# UPLOAD_FOLDER =  'D:/defect_checker_code/app/static/uploads'
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # ✅ 예측 실행
            predicted_class = predict_image(filepath)
            keywords = get_defect_keywords(predicted_class)

            # ✅ Gemini 프롬프트 생성
            # prompt = f"""
            # 다음 하자 클래스는 '{predicted_class}'입니다.
            # 관련된 세부 하자 키워드는 다음과 같습니다: {', '.join(keywords)}.

            # 이 하자의 원인, 위험성, 해결 방법, 입주자에게 필요한 조치사항을 설명해 주세요.
            # """
            prompt = f"""
            다음은 하자 점검 이미지에 대한 분석 결과입니다.

            - 분류된 하자 유형: {predicted_class}
            - 해당 유형의 세부 하자 항목 후보들: {', '.join(keywords) if keywords else '없음'}

            **아래 형식을 반드시 그대로 지켜주세요.**  
            **첫 번째 줄**(세부 항목)과 **두 번째 줄**(위치) 사이에 반드시 줄바꿈(`\\n`)이 들어가야 합니다.

            **예시)**
            코킹 마감 불량 - 
            이미지를 봤을 때 코킹 마감 부위에 코킹 마감 불량이 보입니다.  
            실리콘 마감이 깔끔하게 처리되지 않고 끊어진 부분이 확인됩니다.
            

            위 예시처럼, **실제 이미지에 어떤 하자가 보이는지 구체적으로 추론하여**,
            이렇게 `\n`이 들어간다고 생각하시고,
            `\n` 문자를 쓰지 마시고, 실제 엔터(줄바꿈)만 사용해 주세요. 
            아래 항목을 포함해서 요약해 주세요 (4줄 이내):

            1. 가장 유사해 보이는 세부 하자 항목 1개 선택 예시)코킹 마감 불량 - 
            2. 구체적인 증상 묘사 (이미지 기반 추론처럼)

            
            기술 용어는 유지하되, 불필요한 서론 없이 간단히 설명해 주세요.
            """

            gemini_description = explain_by_gemini(prompt)
            print("gemini response :", gemini_description)
            print("keywords :", keywords)
            return render_template('result.html',
                                   image_name=filename,
                                   predicted_class=predicted_class,
                                   gemini_description=gemini_description)
    return render_template('img_upload.html')
# ---------------------------------------------------------







if __name__ == "__main__":
    app.run(debug=True)