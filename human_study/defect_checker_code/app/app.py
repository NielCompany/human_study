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
from src.model.predict import predict_image

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
            print(filepath)
            # ✅ 예측 실행
            predicted_class = predict_image(filepath)

            return render_template('result.html',
                                   image_name=filename,
                                   predicted_class=predicted_class)
    return render_template('img_upload.html')
# ---------------------------------------------------------







if __name__ == "__main__":
    app.run(debug=True)