 #*******************************************************
 # PY24 課題1 【MySQL接続】
 # CLASS : IH-12A-405(16) NAME : goto akio
 #-------------------------------------------------------
 # 2024-10-16
 #*******************************************************
from flask import Flask,render_template, make_response, request, session, redirect, send_file
from werkzeug.datastructures import FileStorage
import mysql.connector
from datetime import datetime,timedelta
import os
from datetime import datetime
from pathlib import Path

import json
import csv


# 各種変数初期化
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2097152

app.secret_key = 'IH12xPY24_No08'
app.permanent_session_lifetime = timedelta(hours=3)

ALLOW_MIMETYPES = { "gif", "jpeg", "jpg", "png" }

LOGIN_FIELD = {
  "userid": "ユーザーID",
  "password": "パスワード"
}

ONE_HYOTEI = {
  "gno": "学籍番号"
}

MODINPUT = {
  "gno": "学籍番号",
  "ih22": "ih22",
  "py24": "py24",
  "io21": "io21"
}

NEW_HYOTEI = {
  "gno": "学籍番号",
  "cls": "クラス記号",
  "sno": "出席番号",
  "gname": "学生名",
  "ih22": "ih22",
  "py24": "py24",
  "io21": "io21"
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
def get_hyotei_all():
  return query(f"SELECT * FROM hyotei ORDER BY cls ASC, sno ASC;")

def getHyoteiByGno(gno):
  users = query(f"SELECT * FROM hyotei WHERE gno = {gno};")
  if len(users) != 0:
    return users[0]
  else:
    return None

def getLoggedIn():
  return session.get('loggedIn')

def setLoggedIn(user):
  session['loggedIn'] = user

def get_cart():
  cart = request.cookies.get('cart')

  if cart is None:
    return []

  return json.loads(cart)

def set_cart(cart):
  request.cookies.setdefault("cart", )

def judgeResult(ih22, py24, io21):
  if int(ih22) >= 60 and int(py24) >= 60 and int(io21) >= 60:
    return "認定"
  else:
    return "追試"

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
    user = "root" if os.path.exists("/.dockerenv") else "py24user",
    passwd = "root" if os.path.exists("/.dockerenv") else "py24pass",
    db = "py24db" if os.path.exists("/.dockerenv") else "py24db",
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

#****************************************************
#（"/"）
#****************************************************
# @app.route("/")
# def index():

#   return render_template("index.html")


@app.route("/login", methods=["get"])
def login():
  return render_template("login.html", LOGIN_FIELD = LOGIN_FIELD, errors = {}, values = {}, error = "")

@app.route("/login/send", methods=["post"])
def login_send():
  (values, errors) = validate(LOGIN_FIELD, request.form)
  if len(errors.items()) != 0:
    return render_template("login.html", LOGIN_FIELD = LOGIN_FIELD, errors = errors, values = values, error = "")
  else:
    userid = values["userid"]
    password = values["password"]
    users = query(f"SELECT * FROM user WHERE userid = '{userid}' AND userps = '{password}';")

    if len(users) == 0:
      return render_template("login.html", LOGIN_FIELD = LOGIN_FIELD, errors = errors, values = values, error = "ユーザー名またはパスワードが違います。")

    user = users[0]

    setLoggedIn(user)

    return redirect('/')

@app.route("/logout", methods=["post"])
def logout():
  session.clear()
  res = make_response(redirect('/login'))
  res.delete_cookie('cart')

  return res

@app.route("/", methods=["get"])
def index():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")

  hyoteis = get_hyotei_all()

  return render_template("index.html", loggedInUser = user, hyoteis = hyoteis)


@app.route("/modinp", methods=["get"])
def modinp():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")

  gno = request.args.get('gno')
  hyotei = getHyoteiByGno(gno)

  return render_template("modinp.html", loggedInUser = user, hyotei = hyotei, values = {}, errors = {})

@app.route("/input", methods = ["get"])
def input():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")

  return render_template("input.html", NEW_HYOTEI = NEW_HYOTEI, loggedInUser = user, values = {}, errors = {})

@app.route("/upload", methods = ["post"])
def upload():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")
  
  (values, errors) = validate(NEW_HYOTEI, request.form)

  if len(errors.items()) != 0:
    return render_template("input.html", NEW_HYOTEI = NEW_HYOTEI, loggedInUser = user, values = values, errors = errors)

  gno = values["gno"]
  cls = values["cls"]
  sno = values["sno"]
  gname = values["gname"]
  ih22 = values["ih22"]
  py24 = values["py24"]
  io21 = values["io21"]
  judge = judgeResult(ih22, py24, io21)

  execute(f"INSERT INTO `hyotei` (`gno`, `cls`, `sno`, `gname`, `ih22`, `py24`, `io21`, `result`) VALUES ('{gno}', '{cls}', '{sno}', '{gname}', {ih22}, {py24}, {io21}, '{judge}');")

  hyotei = getHyoteiByGno(gno)

  return render_template("upload.html", hyotei = hyotei, loggedInUser = user, values = values)


@app.route("/modinp/send", methods=["post"])
def modinp_send():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")
  
  (values, errors) = validate(MODINPUT, request.form)

  gno = request.form.get('gno')
  hyotei = getHyoteiByGno(gno)

  if not (values.get("ih22") is None):
    hyotei["ih22"] = values["ih22"]

  if not (values.get("py24") is None):
    hyotei["py24"] = values["py24"]

  if not (values.get("io21") is None):
    hyotei["io21"] = values["io21"]

  if len(errors.items()) != 0:
    return render_template("modinp.html", loggedInUser = user, hyotei = hyotei, values = values, errors = errors)

  result = judgeResult(values["ih22"], values["py24"], values["io21"])

  ih22_point = values["ih22"]
  py24_point = values["py24"]
  io21_point = values["io21"]

  execute(f"UPDATE hyotei SET ih22 = {ih22_point}, py24 = {py24_point}, io21 = {io21_point}, result = '{result}' WHERE gno = {gno}; ")

  hyotei = getHyoteiByGno(gno)

  return render_template('update.html', hyotei = hyotei, loggedInUser = user)

@app.route("/cart/add", methods=["post"])
def card_add():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")

  gno = request.form.get('gno')

  cart = get_cart()

  is_exists = False


  for cart_gno in cart:
    print(cart_gno, cart)
    if gno == cart_gno:
      is_exists = True

  if is_exists:
    return render_template("message.html", loggedInUser = user, title = "選択学生情報", message = "学生がすでに追加されています。")
  cart.append(gno)

  hyotei = getHyoteiByGno(gno)
  limit = 60
  expires = int(datetime.now().timestamp()) + limit

  res = make_response(render_template("cart.html", hyotei = hyotei, loggedInUser = user))
  res.set_cookie("cart", value=json.dumps(cart), expires=expires)

  return res

@app.route("/cart/disp", methods=["get"])
def cart_disp():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")

  cart = get_cart()
  print(cart)
  if len(cart) == 0:
    return render_template("message.html", loggedInUser = user, title = "選択学生情報", message = "選択された学生は存在しません")

  students = ",".join(map(map_array_literal, cart))

  hyoteis = query(f"SELECT * FROM hyotei WHERE gno IN ({students}) ORDER BY cls ASC, sno ASC;;")

  return render_template("cart_disp.html", loggedInUser = user, hyoteis = hyoteis, gnos = students)

@app.route("/cart/clear", methods=["post"])
def cart_clear():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")

  res = make_response(render_template("message.html", loggedInUser = user, title = "選択学生情報", message = "選択された学生をクリアしました"))
  res.delete_cookie("cart")

  return res

def map_array_literal(entry):
  return f"\'{entry}\'"

@app.route("/download/all", methods=["get"])
def donwload_all():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")

  file_path = os.path.dirname(__file__) + "/" + "csvout.csv"
  with open(file_path, 'w', encoding='utf-8', newline='') as outfile:
    csvout = csv.writer(outfile)
    #*** CSV出⼒⽤レコード作成 ***
    for tbl in get_hyotei_all():
      csvt = []
      for value in tbl.values():
        csvt.append(value)
        #*** CSVレコード出⼒ ***

      csvout.writerow(csvt)
  return send_file(file_path, as_attachment=True)


@app.route("/download/filterd", methods=["get"])
def donwload_filtered():
  user = getLoggedIn()
  if user is None:
    return redirect("/login")

  cart = request.args.get("targets")

  hyoteis = query(f"SELECT * FROM hyotei WHERE gno IN ({cart}) ORDER BY cls ASC, sno ASC;")

  file_path = os.path.dirname(__file__) + "/" + "csvout.csv"
  with open(file_path, 'w', encoding='utf-8', newline='') as outfile:
    csvout = csv.writer(outfile)
    #*** CSV出⼒⽤レコード作成 ***
    for tbl in hyoteis:
      csvt = []
      for value in tbl.values():
        csvt.append(value)
        #*** CSVレコード出⼒ ***

      csvout.writerow(csvt)
  return send_file(file_path, as_attachment=True)


#****************************************************
# アプリケーション実⾏
#****************************************************
if __name__ == "__main__":
  app.debug=False #開発時デバックMODE
  app.run(host="0.0.0.0", port=5000)
