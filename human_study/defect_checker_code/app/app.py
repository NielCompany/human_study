# 추후 웹 앱용 진입점 (Flask or Streamlit)
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from werkzeug.security import generate_password_hash, check_password_hash
from db import user_util
# from werkzeug.utils import secure_filename
# from model.predict import predict_defect_class  # 예측 함수
# from utils.gemini_utils import explain_by_gemini  # Gemini 설명 함수

# upload_bp = Blueprint("upload", __name__)



# app = create_app()
app = Flask(__name__)
app.secret_key = "your-secret-key"  # 세션 유지에 필요

## index rendering 
@app.route("/")
def index():
    return render_template("index.html")



# -------------------------------
# 로그인
# -------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get('email', '')
    passwd = request.form.get('passwd', '')

    user = user_util.select_user_by_email(email)
    if not user or not check_password_hash(user[2], passwd):
        flash("이메일 또는 비밀번호가 일치하지 않습니다.")
        return redirect(url_for('login'))

    session['loginuser'] = user[1]  # email
    username = user[3]              # username
    flash(f"{username}님 반갑습니다!")
    return redirect(url_for('index'))


# -------------------------------
# 회원가입 
# -------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    # 폼 데이터 수집
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    passwd = request.form.get("passwd", "").strip()

    # ✅ 유효성 검사
    if not username or not email or not passwd:
        flash("모든 항목을 입력해주세요.")
        return render_template("auth/register.html")

    # 비밀번호 최소 길이 검사
    if len(passwd) < 6:
        flash("비밀번호는 최소 6자 이상이어야 합니다.")
        return render_template("auth/register.html")

    # 비밀번호 해시
    passwd_hash = generate_password_hash(passwd)

    # 사용자 등록 시도
    success = user_util.insert_user(email, passwd_hash, username)
    if not success:
        flash("이미 등록된 이메일입니다.")
        return render_template("auth/register.html")

    flash("회원가입이 완료되었습니다.")
    return redirect(url_for("login"))

# -------------------------------
# 로그아웃
# -------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# -------------------------------
# chatbot 
# -------------------------------
from utils.gemini_utils import ask_gemini  

@app.route("/chat", methods=["POST"])
def chat_api():
    user_message = request.json.get("message", "")
    bot_reply = ask_gemini(user_message)
    return jsonify({"reply": bot_reply})


# -------------------------------
# ABOUT US 
# -------------------------------

## index rendering 
@app.route("/about")
def about():
    return render_template("about.html")

# predict----------------------------------------------------------------------------------------

from werkzeug.utils import secure_filename
from src.model.predict import predict_image, get_defect_keywords
# from utils.gemini_utils import explain_by_gemini  # Gemini API 호출 함수
from utils.gpt4o_utils import explain_by_gpt4o_with_image
import os

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            predicted_class = predict_image(filepath)
            keywords = get_defect_keywords(predicted_class)


            prompt = f"""
            다음은 하자 점검 이미지에 대한 분석 결과입니다.

            - 분류된 하자 유형: {predicted_class}
            - 해당 유형의 세부 하자 항목 후보들: {', '.join(keywords) if keywords else '없음'}

            **아래 형식을 반드시 그대로 지켜주세요.**  
            **첫 번째 줄**(세부 항목)과 **두 번째 줄**(위치) 사이에 반드시 줄바꿈(`\n`)이 들어가야 합니다.

            예시)
            코킹 마감 불량 -
            이미지를 봤을 때 코킹 마감 부위에 코킹 마감 불량이 보입니다.  
            실리콘 마감이 깔끔하게 처리되지 않고 끊어진 부분이 확인됩니다.

            위 예시처럼, **실제 이미지에 어떤 하자가 보이는지 구체적으로 추론하여**,
            이렇게 `\n`이 들어간다고 생각하시고,
            `\n` 문자를 쓰지 마시고, 실제 엔터(줄바꿈)만 사용해 주세요. 
            아래 항목을 포함해서 요약해 주세요 (4줄 이내):

            1. 가장 유사해 보이는 세부 하자 항목 1개 선택 예시)코킹 마감 불량 - 
            2. 구체적인 증상 묘사 (이미지 기반 추론처럼)

            
            기술 용어는 유지하되, 불필요한 서론 없이 간단히 존댓말로 설명해 주세요.
            정확하지 않은 부분에 대해서는 서술하지 않으셔야 합니다.
            정확한 내용만 설명해주세요.
            띄어쓰기 및 줄바꿈 처리도 깔끔하게 해주세요.

            """
            

            gpt4o_description = explain_by_gpt4o_with_image(filepath, prompt)

            return render_template('result.html',
                                   image_name=filename,
                                   predicted_class=predicted_class,
                                   gemini_description=gpt4o_description)
    return render_template('img_upload.html')
# # ---------------------------------------------------------

# predict ( Model 이 분류해준 predict 반환 안받고 prompt 짠거 )

# from werkzeug.utils import secure_filename
# from src.model.predict import predict_image, get_defect_keywords
# # from utils.gemini_utils import explain_by_gemini  # Gemini API 호출 함수
# from utils.gpt4o_utils import explain_by_gpt4o_with_image
# import os

# UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# classes = [
#     "개폐 불량","고정 불량","균열","누수","도배 불량","도장 불량","랩핑 불량","마감 불량","마루 불량",
#     "문틀 불량","벽체 불량","수직 및 수평 불량","수직 수평 불량","수평 불량","시공 불량",
#     "시공 확인 필요","없음","오염","자재 불량","줄눈 마감 불량","코킹 불량","타공 불량","타일 불량"
# ]

# mapping_data = """
#             도배 불량 : 도배 마감 불량, 도배 주름짐, 도배 면 불량, 도배 조인트 불량, 도배 태움 불량, 도배 오염, 도배 들뜸, 도배 요철, 도배 찢김
#             타일 불량 : 타일 채움 불량, 타일 오염, 타일 들뜸, 타일 손상, 타일 구배 불량, 타일 오타공, 타일 줄눈 마감 불량
#             마루 불량 : 마루 들뜸, 마루 수평 불량, 마루 틈새, 마루 단차
#             코킹 불량 : 코킹 마감 불량, 코킹 오염, 코킹 미시공
#             자재 불량 : 자재 오염, 자재 불량, 자재 손상, 자재 미시공, 자재 고정 불량, 수평 불량, 수직 불량, 수평 수직 불량, 자재 틈새, 자재 맞춤 불량, 자재 재단 불량, 자재 도장 오염, 자재 오타공, 자재 단차, 자재 줄눈 마감 불량, 자재 조인트 불량, 자재 단차, 씰 손상
#             랩핑 불량 : 랩핑 들뜸, 랩핑 손상, 랩핑 오염
#             문틀 불량 : 문틀 오염, 문틀 고정 불량, 문틀 도장 불량, 문틀 도장 오염, 문틀 틀어짐
#             창틀 불량 : 창틀 흔들림, 창틀 틈새, 창틀 오염, 창틀 도장 오염
#             벽면 불량 : 벽면 도장 불량
#             벽체 불량 : 벽체 오타공, 벽체 틀어짐, 벽체 고정 불량, 평활도 불량
#             창호 불량 : 창호 오타공
#             천장 불량 : 천장 오타공, 천장 시공 불량, 천장 마감 불량
#             수직 및 수평 불량 : 수직 불량, 수평 불량, 수직 수평 불량, 레벨 확인 필요
#             타공 불량 : 타공 마감 불량, 오타공, 타공 마감 누락
#             줄눈 마감 불량
#             시공 불량 : 시공 불량 - 틈새, 시공 불량 - 유격, 시공 불량 - 개폐 불량, 시공 불량 - 수평, 시공 불량 - 수직, 시공 불량 - 수직 및 수평, 시공 불량 - 수평 및 수직, 시공 불량 - 면처리 불량, 시공 불량 - 도장 불량, 시공 마감 요망, 시공 불량 - 평활도 불량, 시공 불량 - 구배 불량, 시공 불량 - 줄눈 불량, 시공 불량 - 줄눈 누락, 시공 불량 - 채움 불량, 시공 불량 - 사춤 불량, 시공 불량 - 창틀 흔들림
#             시공 확인 필요
#             마감 불량 : 마감 누락, 마감 불량, 마감 요망
#             개폐 불량
#             균열
#             누수
#             사춤 불량
#             """

# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     if request.method == 'POST':
#         file = request.files['image']
#         if file:
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(UPLOAD_FOLDER, filename)
#             file.save(filepath)

#             prompt = f"""
#             너는 전문가이며, 사용자가 제공한 이미지를 분석해 하자 유형을 추론해야 합니다.
#             아래 클래스 정보를 참고하여 가장 가능성 높은 하자 유형과 설명을 생성해야 합니다.

#             📌 참고할 수 있는 하자 대분류: {classes}
#             📌 해당 대분류별 세부 분류 정보: {mapping_data}

#             아래 예시처럼 출력 형식을 지켜주세요:

#             예시)
#             대분류 : 코킹 마감 불량
#             이미지를 봤을 때 코킹 마감 부위에 코킹 마감 불량이 보입니다.
#             실리콘 마감이 깔끔하게 처리되지 않고 끊어진 부분이 확인됩니다.

#             🔹 반드시 위와 같은 형식으로 출력할 것
#             🔹 실제 이미지에 보이는 것처럼 묘사하되, 전문가의 시각에서 **가장 가능성 높은** 판단을 해줄 것
#             🔹 4줄 이내로 요약할 것
#             """
            
#             gpt4o_description = explain_by_gpt4o_with_image(filepath, prompt)

#             return render_template('result.html',
#                                    image_name=filename,
#                                    gemini_description=gpt4o_description)
#     return render_template('img_upload.html')





if __name__ == "__main__":
    app.run(debug=True)