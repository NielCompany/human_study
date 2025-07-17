# 추후 웹 앱용 진입점 (Flask or Streamlit)
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
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

    # ✅ 사용자 정보 세션에 저장
    session['loginuser'] = {
        "id": user[0],
        "email": user[1],
        "username": user[3]
    }

    flash(f"{user[3]}님 반갑습니다!")
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
    return redirect(url_for("index", cleared="true"))

# -------------------------------
# chatbot 
# -------------------------------
from utils.gemini_utils import ask_gemini  
from utils.rag_utils import answer_with_rag  
# @app.route("/chat", methods=["POST"])
# def chat_api():
#     user_message = request.json.get("message", "")
#     bot_reply = ask_gemini(user_message)
#     return jsonify({"reply": bot_reply})

# 

@app.route("/chat", methods=["POST"])
def chat_api():
    user_message = request.json.get("message", "")
    bot_reply = answer_with_rag(user_message)
    return jsonify({"reply": bot_reply})


# -------------------------------
# ABOUT US 
# -------------------------------

## about rendering 
@app.route("/about")
def about():
    return render_template("about.html")


##  board
from db import board_util

@app.route("/board")
def board_list():
    page = int(request.args.get('page', 1))  # 기본값 1
    per_page = 10

    posts, total = board_util.get_posts_by_page(page, per_page)
    total_pages = (total + per_page - 1) // per_page

    return render_template("board/board_list.html",
                           posts=posts,
                           page=page,
                           total_pages=total_pages)

## 게시글 작성 
@app.route("/board/write", methods=["GET", "POST"])
def board_write():
    if 'loginuser' not in session:
        flash("로그인 후 글쓰기가 가능합니다.")
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("board/board_write.html")

    # POST 처리 (제목, 내용 저장)
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    user_id = session["loginuser"]["id"]

    print("POST 요청 수신됨:", data, )

    if not title or not content:
        return jsonify({"message": "제목과 내용을 모두 입력해주세요."}), 400

    success = board_util.insert_post(user_id, title, content)
    if not success:
        return jsonify({"message": "글쓰기 중 오류가 발생했습니다."}), 500

    return jsonify({"message": "글이 성공적으로 작성되었습니다."})

# 게시글 내용에 img 포함 될 때 
@app.route("/board/upload_image", methods=[ "POST"])
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400

    file = request.files["file"]
    filename = secure_filename(file.filename)
    save_path = os.path.join("static", "board_uploads", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    file.save(save_path)

    file_url = url_for('static', filename=f'board_uploads/{filename}')
    return jsonify({"url": file_url})

# -------------------------------
# 게시글 상세보기
# -------------------------------
@app.route("/board/<int:post_id>")
def board_detail(post_id):
    if "loginuser" not in session:
        flash("로그인 후 이용 가능합니다.")
        return redirect(url_for("login"))

    post = board_util.get_post_by_id(post_id)
    if not post:
        flash("해당 게시글이 존재하지 않습니다.")
        return redirect(url_for("board_list"))

    # 조회수 증가 (한 번만)
    board_util.increase_view_count(post_id)

    # 현재 로그인한 유저ID
    current_user_id = session["loginuser"]["id"]
    return render_template("board/board_detail.html", post=post, current_user_id=current_user_id)

# -------------------------------
# 게시글 수정 페이지 출력 및 저장
# -------------------------------
@app.route("/board/<int:post_id>/edit", methods=["GET", "POST"])
def board_edit(post_id):
    if "loginuser" not in session:
        flash("로그인 후 이용 가능합니다.")
        return redirect(url_for("login"))

    post = board_util.get_post_by_id(post_id)
    if not post:
        flash("해당 게시글이 존재하지 않습니다.")
        return redirect(url_for("board_list"))

    current_user_id = session["loginuser"]["id"]
    if post["user_id"] != current_user_id:
        flash("해당 게시글을 수정할 수 없습니다.")
        return redirect(url_for("board_detail", post_id=post_id))

    if request.method == "GET":
        return render_template("board/board_edit.html", post=post)

    # POST (AJAX)
    data = request.get_json()
    if data is None:
        return jsonify({"message": "잘못된 요청입니다."}), 400

    title = data.get("title")
    content = data.get("content")
    if not title or not content:
        return jsonify({"message": "제목과 내용을 모두 입력해주세요."}), 400

    success = board_util.update_post(post_id, title, content)
    if not success:
        return jsonify({"message": "수정 중 오류가 발생했습니다."}), 500

    return jsonify({"message": "게시글이 수정되었습니다."})

# -------------------------------
# 게시글 삭제 (소프트 삭제)
# -------------------------------
@app.route("/board/<int:post_id>/delete", methods=["POST"])
def board_delete(post_id):
    if "loginuser" not in session:
        return jsonify({"message": "로그인 후 이용 가능합니다."}), 401

    post = board_util.get_post_by_id(post_id)
    if not post:
        return jsonify({"message": "해당 게시글이 존재하지 않습니다."}), 404

    current_user_id = session["loginuser"]["id"]
    if post["user_id"] != current_user_id:
        return jsonify({"message": "삭제 권한이 없습니다."}), 403

    success = board_util.delete_post(post_id)
    if not success:
        return jsonify({"message": "삭제 중 오류가 발생했습니다."}), 500

    return jsonify({"message": "삭제되었습니다."})

# predict----------------------------------------------------------------------------------------

# from werkzeug.utils import secure_filename
# from src.model.predict import predict_image, get_defect_keywords
# # from utils.gemini_utils import explain_by_gemini  # Gemini API 호출 함수
# from utils.gpt4o_utils import explain_by_gpt4o_with_image, client
# import os

# UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)



# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     if request.method == 'POST':
#         file = request.files.get('image')
#         if not file:
#             return render_template('img_upload.html', error="이미지를 업로드해주세요.")

#         # 1) 파일 저장
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(UPLOAD_FOLDER, filename)
#         file.save(filepath)

#         # 2) 기본 분류
#         predicted_class = predict_image(filepath)
#         keywords = get_defect_keywords(predicted_class)

#         # 3) 원본 프롬프트(상세 지시) 그대로 사용
#         prompt = f"""
#         다음은 하자 점검 이미지에 대한 분석 결과입니다.

#         - 분류된 하자 유형: {predicted_class}
#         - 해당 유형의 세부 하자 항목 후보들: {', '.join(keywords) if keywords else '없음'}

#         **아래 형식을 반드시 그대로 지켜주세요.**  
#         **첫 번째 줄**(세부 항목)과 **두 번째 줄**(위치) 사이에 반드시 줄바꿈(`\n`)이 들어가야 합니다.

#         예시)
#         코킹 마감 불량 -
#         이미지를 봤을 때 코킹 마감 부위에 코킹 마감 불량이 보입니다.  
#         실리콘 마감이 깔끔하게 처리되지 않고 끊어진 부분이 확인됩니다.

#         위 예시처럼, **실제 이미지에 어떤 하자가 보이는지 구체적으로 추론하여**,
#         이렇게 `\n`이 들어간다고 생각하시고,
#         `\n` 문자를 쓰지 마시고, 실제 엔터(줄바꿈)만 사용해 주세요. 
#         아래 항목을 포함해서 요약해 주세요 (4줄 이내):

#         1. 가장 유사해 보이는 세부 하자 항목 1개 선택 예시)코킹 마감 불량 - 
#         2. 구체적인 증상 묘사 (이미지 기반 추론처럼)

#         기술 용어는 유지하되, 불필요한 서론 없이 간단히 존댓말로 설명해 주세요.
#         정확하지 않은 부분에 대해서는 서술하지 않으셔야 합니다.
#         정확한 내용만 설명해주세요.
#         띄어쓰기 및 줄바꿈 처리도 깔끔하게 해주세요.
#         """

#         # 4) 첫 번째 GPT-4o 호출: 상세 설명 생성
#         gpt4o_description = explain_by_gpt4o_with_image(filepath, prompt)

#         # 5) 두 번째 GPT-4o 호출: yes/no로 하자 유무 확인
#         confirm = client.chat.completions.create(
#             model="gpt-4o",
#             messages=[{
#                 "role": "user",
#                 "content": (
#                     "아래 설명이 실제 하자 설명인가요? 하자가 없으면 '아니오', 있으면 '예'라고만 답해주세요.\n\n"
#                     f"{gpt4o_description}"
#                 )
#             }],
#             temperature=0
#         )
#         answer = confirm.choices[0].message.content.strip()

#         # 6) '아니오'면 predicted_class만 '없음'으로 변경
#         if answer.startswith("아니오"):
#             predicted_class = "없음"

#         # 7) 세션에 결과 저장
#         session['last_image'] = filename
#         session['last_prediction'] = {
#             'category': predicted_class,
#             'description': gpt4o_description
#         }

#         # 7) 최종 렌더링
#         return render_template(
#             'result.html',
#             image_name=filename,
#             predicted_class=predicted_class,
#             gemini_description=gpt4o_description
#         )

#     return render_template('img_upload.html')

#-------------------------------------------multi_predict 
from werkzeug.utils import secure_filename
from src.model.predict import predict_image, get_defect_keywords
from utils.gpt4o_utils import explain_by_gpt4o_with_image, client
import os

from pathlib import Path
from datetime import datetime

# UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# UPLOAD_FOLDER를 Path 객체로
UPLOAD_FOLDER = Path(app.root_path) / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)



@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        files = request.files.getlist('images')
        print("files",files)
        if not files or files[0].filename == '':
            return render_template('multi_img_upload.html', error="이미지를 업로드해주세요.")

        results = []
        print("DEBUG: 업로드된 파일 개수 =", len(files))

        for idx, file in enumerate(files, start=1):
            filename = secure_filename(file.filename)
           # filepath = os.path.join(UPLOAD_FOLDER, filename)
            filepath: Path = UPLOAD_FOLDER / filename
            file.save(filepath)
            print(f"DEBUG [{idx}] saved file →", filename)

            # 2) 기본 분류
            predicted_class = predict_image(filepath)
            keywords = get_defect_keywords(predicted_class)
            print(f"DEBUG [{idx}] predicted_class =", predicted_class)
            print(f"DEBUG [{idx}] keywords =", keywords)

            # 3) GPT-4o 호출
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
            print(f"DEBUG [{idx}] gpt4o_description =", gpt4o_description)

            # 4) yes/no 검증
            confirm = client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": (
                        "아래 설명이 실제 하자 설명인가요? 하자가 없으면 '아니오', 있으면 '예'라고만 답해주세요.\n\n"
                        f"{gpt4o_description}"
                    )
                }],
                temperature=0
            )
            answer = confirm.choices[0].message.content.strip()
            print(f"DEBUG [{idx}] answer =", answer)
            if answer.startswith("아니오"):
                predicted_class = "없음"

            # 5) 결과 리스트에 추가
            results.append({
                'image_name': filename,
                'predicted_class': predicted_class,
                'description': gpt4o_description
            })
            print(f"DEBUG [{idx}] appended to results")

            session['last_results'] = results
            session['report_time']  = datetime.now().strftime("%Y-%m-%d %H:%M")
            
        # 루프 끝난 뒤에 한 번만 전체 results 출력
        print("DEBUG: Final results list:", results)
        

        return render_template('multi_result.html', results=results)

    return render_template('multi_img_upload.html')

##--------------------------------------------------------------
# OCR_EXTRACT
# -------------------------------
from pathlib import Path
import uuid, time, json, requests
from dotenv import load_dotenv
from flask import session, request, redirect, url_for, render_template, make_response, send_file

from datetime import datetime

# 환경변수 로드 및 검증
load_dotenv()
CLOVA_API_KEY = os.getenv("CLOVA_API_KEY")
API_URL = os.getenv("CLOVA_API_URL")
if not CLOVA_API_KEY or not API_URL:
    raise RuntimeError("환경 변수 오류: CLOVA_API_URL과 CLOBA_API_KEY를 .env 파일에 정확히 설정해주세요.")

#  키-값 추출 함수
def extract_key_value_by_row(fields, row_threshold=15):
    items = []
    for f in fields:
        verts = f['boundingPoly']['vertices']
        # convert missing coords
        verts = [{ 'x': v.get('x',0), 'y': v.get('y',0) } for v in verts]
        top = min(p['y'] for p in verts)
        left = min(p['x'] for p in verts)
        items.append({ 'text': f['inferText'].strip(), 'top': top, 'left': left, 'bbox': verts })
    items.sort(key=lambda x: (x['top'], x['left']))
    rows, cur = [], []
    for it in items:
        if not cur or abs(it['top'] - cur[0]['top']) <= row_threshold:
            cur.append(it)
        else:
            rows.append(cur)
            cur = [it]
    if cur: rows.append(cur)
    pairs = []
    for row in rows:
        row = sorted(row, key=lambda x: x['left'])
        if len(row) >= 2:
            key = row[0]['text'].replace(' ', '')
            val = ' '.join(r['text'] for r in row[1:])
        else:
            key = row[0]['text'].replace(' ', '')
            val = ''
        pairs.append((key, val))
    return pairs

#  OCR 호출
def run_ocr(image_path: Path):
    payload = {
        'images': [{'format': image_path.suffix[1:], 'name': image_path.name}],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(time.time()*1000)
    }
    files = [('file', open(image_path, 'rb'))]
    headers = {'X-OCR-SECRET': CLOVA_API_KEY}
    data = {'message': json.dumps(payload).encode('UTF-8')}
    resp = requests.post(API_URL, headers=headers, data=data, files=files, timeout=30)
    resp.raise_for_status()
    return resp.json()

SESSION_KEY = 'ocr_results'


@app.route("/ocr/upload", methods=["GET", "POST"])
def ocr_upload():
    # 1) GET: 업로드 폼 보여주기
    if request.method == "GET":
        session.pop("ocr_results", None)
        return render_template("ocr_upload.html")  # 친구분의 upload.html 혹은 ocr_upload.html

    # 2) POST: 파일 처리
    files = request.files.getlist("photos")  # input name="photos"로 맞춰 주세요
    out = []
    for f in files:
        # 2-1) 파일 저장
        UPLOAD_FOLDER = Path(app.root_path) / "static" / "uploads"
        save_path = UPLOAD_FOLDER / f.filename
        f.save(save_path)

        # 2-2) OCR 호출 & 키-값 정리
        try:
            raw = run_ocr(save_path)
            fields = raw["images"][0]["fields"]
            pairs = extract_key_value_by_row(fields)
            # fallback: 콜론 파싱
            if not pairs:
                pairs = [
                    tuple(line.split(":",1))
                    for line in (x["inferText"] for x in fields)
                    if ":" in line
                ]
        except Exception:
            pairs = []

        # 2-3) 세션에 담을 구조로 포장
        out.append({
            "filename": f.filename,
            "pairs": pairs,
            # PDF 템플릿에서 바로 쓸 수 있게 URL까지 추가
            "image_url": url_for("static",
                                  filename=f"uploads/{f.filename}",
                                  _external=True)
        })

    # 3) 세션에 저장
    session["ocr_results"] = out

    # 4) 결과 페이지 혹은 PDF 다운로드 페이지로 리다이렉트
    #    바로 PDF로 보내고 싶으면 url_for('download_ocr_pdf')로 바꾸세요.
    return redirect(url_for("show_ocr_results"))

@app.route("/ocr/results")
def show_ocr_results():
    results = session.get("ocr_results")
    if not results:
        return redirect(url_for("ocr_upload"))
    return render_template("report.html", results=results)

@app.route("/ocr/download_pdf")
def download_ocr_pdf():
    from weasyprint import HTML
    results = session.get("ocr_results", [])
    if not results:
        return "먼저 OCR 수행 후 시도해주세요.", 400

    html_str = render_template(
        "simple_report.html",   # 친구분 템플릿
        now=datetime.now().strftime("%Y-%m-%d %H:%M"),
        results=results
    )
    pdf_bytes = HTML(string=html_str).write_pdf()

    resp = make_response(pdf_bytes)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = \
        "attachment; filename=ocr_report.pdf"
    return resp

# ----------------결과 word 파일로 저장----------------------

import docx
from docx import Document
from docx.shared import Inches
from io import BytesIO
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

@app.route('/report/docx')
def download_docx():
    # 세션에서 결과 불러오기
    results = session.get('ocr_results', [])
    if not results:
        return "먼저 이미지 예측을 수행해주세요.", 400

    # Document 객체 생성
    doc = Document()
    doc.add_heading('AI 하자 진단 리포트', level=1)
    doc.add_paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"))

    # 테이블 생성 (헤더 포함, 2열)
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'  
    table.allow_autofit = False
    hdr = table.rows[0].cells
    hdr[0].text = '이미지'
    hdr[1].text = '추출 결과'

    # 각 결과마다 새 행 추가
    for item in results:
        row_cells = table.add_row().cells
        # --- 셀 분할 방지 (한/글에 복사해도 행이 잘리지 않도록) ---
        tr = row_cells[0]._tc.getparent()    # 행( w:tr ) 요소
        trPr = tr.get_or_add_trPr()          # w:trPr
        cantSplit = OxmlElement('w:cantSplit')
        trPr.append(cantSplit)

        # 2) 이미지 넣기
        paragraph = row_cells[0].paragraphs[0]
        run = paragraph.add_run()
        run.add_picture(
            str(UPLOAD_FOLDER / item['filename']),
            width=Inches(2)
        )

        # 3) 텍스트 넣고 단락마다 KeepTogether 설정
        texts = [f"{k} : {v}" for k, v in item['pairs']]
        for idx, line in enumerate(texts):
            p = row_cells[1].add_paragraph(line)
            p.paragraph_format.keep_together = True
            if idx < len(texts)-1:
                p.paragraph_format.keep_with_next = True

    # 메모리 버퍼에 저장
    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)

    return send_file(
        buf,
        as_attachment=True,
        download_name='ocr_report.docx',
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )


# # ---------------------------------------------------------

from datetime import datetime
import os

@app.route('/report/pdf')
def download_pdf():
    from weasyprint import HTML
    results    = session.get('last_results')
    report_time= session.get('report_time')
    if not results:
        return "먼저 예측을 수행해주세요.", 400

    # 각 이미지에 대한 외부 URL 생성
    items = []
    for r in results:
        items.append({
            'image_url': url_for('static', filename=f'uploads/{r["image_name"]}', _external=True),
            'category' : r['predicted_class'],
            'description': r['description'],
        })

    html_str = render_template(
        'multi_report.html',
        now=report_time,
        items=items
    )
    pdf_bytes = HTML(string=html_str).write_pdf()
    resp = make_response(pdf_bytes)
    resp.headers['Content-Type'] = 'application/pdf'
    resp.headers['Content-Disposition'] = 'attachment; filename=defect_report.pdf'
    return resp



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
    app.run(debug=True, use_reloader=False)