 #*******************************************************
 # PY24 課題1 【MySQL接続】
 # CLASS : IH-12A-405(16) NAME : goto akio
 #-------------------------------------------------------
 # 2024-10-16
 #*******************************************************
from flask import Flask,render_template, make_response, request
from werkzeug.datastructures import FileStorage
import mysql.connector
import os
from datetime import datetime
from PIL import Image, ImageFile
from pathlib import Path

# 各種変数初期化
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2097152

ALLOW_MIMETYPES = { "gif", "jpeg", "jpg", "png" }

# fild
fild = {
  "scode":"商品番号",
  "sname":"商品名",
  "price":"商品価格",
  "detail":"商品説明",
}

VIEW_FILES = {
  "scode":"商品番号",
  "sname":"商品名",
  "price":"商品価格",
  "detail":"商品説明",
}

def validate(field, actual):
  errors = {}
  values = {}
  for (key, label) in field.items():
    if actual.get(key) is None or actual.get(key) == "":
      errors[key] = f"{label}が入力されてません。"
    else:
      values[key] = actual[key]

  return (values, errors)

def render_error(message: str, error: Exception, code):
  print(f"********************* システム運用エラー *********************")
  print(error)

  temp = render_template("error.html", message = message, code = code)
  res = make_response(temp, code)

  return res

def query(query):
  recs = None
  
  con = con_db()
  cur = con.cursor(dictionary=True) 
  cur.execute(query)
  recs = cur.fetchall()
  cur.close()
  con.close()

  return recs


def execute(sql):
  recs = None
  
  con = con_db()
  cur = con.cursor()
  cur.execute(sql)
  con.commit()
  cur.close()
  con.close()

  return recs

# DB接続関数
def con_db():
  con = mysql.connector.connect(
    host = "pythondatabase" if os.path.exists("/.dockerenv") else "localhost",
    user = "root",
    passwd = "root",
    db = "py24db",
  )
  return con

def is_accetable_file(file: FileStorage) -> bool:
  ext = file.name.split(".")[-1]
  for allow_ext in ALLOW_MIMETYPES:
    if allow_ext == ext:
      return True
  return False

# エラーハンドラー
@app.errorhandler(404)
def notfound_handler(error):
  return render_error("リクエストされたページは見つかりません。", error, error.code)

@app.errorhandler(413)
def notfound_handler(error):
  return render_error("ファイルのサイズを2MB以内にしてください。", error, error.code)

@app.errorhandler(500)
def server_internal_error_handler(error):
  return render_error("内部サーバーエラーが発生しました。", error, error.code)

# タイムスタンプ生成
def generate_timestamp(dt: datetime) -> str:
  return dt.strftime("%Y%m%d_%H%M%S")

# Resize
def image_reduction(img: ImageFile.ImageFile, maxsize: int) -> Image.Image:
  if img.width > img.height and img.width > maxsize:
    height = int((maxsize / img.width) * img.height)
    return img.resize((maxsize, height))
  elif img.width < img.height and img.height > maxsize:
    width = int((maxsize / img.height) * img.width)
    return img.resize((width, maxsize))
  else:
    return img.copy()

#****************************************************
#（"/"）
#****************************************************
# @app.route("/")
# def index():

#   return render_template("index.html")


@app.route("/", methods=["get"])
def index():
  records = query("SELECT * FROM lunch ORDER BY scode ASC;")
  print(records)
  return render_template('index.html', records=records, VIEW_FILES = VIEW_FILES)

@app.route("/upload", methods=["get"])
def upload():
  return render_template("upload.html", fild=fild, errors={})
@app.route("/upload/complete", methods=["post"])
def upload_img():
  values,errors = validate(fild, request.form)
  
  file = request.files.get("file")

  if not file:
    errors['file'] = "商品画像が選択されていません。"

  if len(errors.keys()) != 0:
    return render_template("upload.html", fild=fild, errors=errors)

  if is_accetable_file(file):
    return render_error("取り扱い不可のファイル種別です。", { "code": 400 })

  img = Image.open(file)
  timestamp = generate_timestamp(datetime.now())
  filename = f"{timestamp}.png"

  execute(f"""
    INSERT INTO lunch (scode, sname, price, detail, filename) VALUES (
      '{values['scode']}',
      '{values['sname']}',
      {values['price']},
      '{values['detail']}',
      '{filename}'
    );
  """)

  normal_img = image_reduction(img, 500)
  thumb_img = image_reduction(img, 1000)

  normal_img.save(
    Path.cwd() / f"static/image/{filename}"
  )

  thumb_img.save(
    Path.cwd() / f"static/image/thumb/{filename}"
  )

  return render_template("detail.html", fild=fild, values=values, filename=filename)

#****************************************************
# アプリケーション実⾏
#****************************************************
if __name__ == "__main__":
  app.debug=False #開発時デバックMODE
  app.run(host="0.0.0.0", port=5000)
