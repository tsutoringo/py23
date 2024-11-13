 #*******************************************************
 # PY24 課題1 【MySQL接続】
 # CLASS : IH-12A-405(16) NAME : goto akio
 #-------------------------------------------------------
 # 2024-10-16
 #*******************************************************
from flask import Flask,render_template, make_response, request
import mysql.connector
import os

# 各種変数初期化
app = Flask(__name__)

# fild
fild = {
  "gno":"学籍番号",
  "gname":"学生名",
  "addr":"住所",
  "tel":"電話番号",
  "detail":"詳細"
}

def render_error(message: str, error: Exception):
  print(f"********************* システム運用エラー *********************")
  print(error)

  temp = render_template("error.html", message = message, code = error.code)
  res = make_response(temp, error.code)

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


# DB接続関数
def con_db():
  con = mysql.connector.connect(
    host = "pythondatabase" if os.path.exists("/.dockerenv") else "localhost",
    user = "root",
    passwd = "roota",
    db = "py24db",
  )
  return con

# エラーハンドラー
@app.errorhandler(404)
def notfound_handler(error):
  return render_error("リクエストされたページは見つかりません。", error)

@app.errorhandler(500)
def server_internal_error_handler(error):
  return render_error("内部サーバーエラーが発生しました。", error)


#****************************************************
#（'/'）
#****************************************************
@app.route('/')
def index():
  recs = query("SELECT * FROM gakuseki;")

  return render_template("index.html", recs=recs, fild=fild)

@app.route('/detail')
def detail():
  gno = request.args["gno"]

  rec = query(f"SELECT * FROM gakuseki where gno = {gno};")[0]

  return render_template("detail.html", rec=rec, fild=fild)

#****************************************************
# アプリケーション実⾏
#****************************************************
if __name__ == "__main__":
  app.debug=False #開発時デバックMODE
  app.run(host="0.0.0.0", port=5000)
