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
  print(type(error))
  print(error)

  temp = render_template("error.html", message = message, code = type(error))
  res = make_response(temp, 500)

  return res

# DB接続関数
def con_db():
  con = mysql.connector.connect(
    host = "pythondatabase" if os.path.exists("/.dockerenv") else "localhost",
    user = "root",
    passwd = "root",
    db = "py24db",
  )
  return con

#****************************************************
#（'/'）
#****************************************************
@app.route('/')
def index():

  recs = None
  
  try:
    sql = "SELECT * FROM gakuseki;"
    con = con_db()
    cur = con.cursor(dictionary=True) 
    cur.execute(sql)
    recs = cur.fetchall()
    cur.close()
    con.close()
  except mysql.connector.errors.DatabaseError as error:
    return render_error("データーベーサーバーの起動が確認できません。", error)
  except mysql.connector.errors.ProgrammingError as error:
    return render_error("データベースプログラミングエラー", error)
  except Exception as error:
    return render_error("予期せぬエラーが発生しました。", error)
  return render_template("index.html", recs=recs, fild=fild)

@app.route('/detail')
def detail():
  gno = request.args["gno"]
  rec = None
  
  try:
    sql = f"SELECT * FROM gakuseki where gno = {gno};"
    con = con_db()
    cur = con.cursor(dictionary=True) 
    cur.execute(sql)
    rec = cur.fetchall()[0]
    cur.close()
    con.close()
  except mysql.connector.errors.DatabaseError as error:
    return render_error("データーベーサーバーの起動が確認できません。", error)
  except mysql.connector.errors.ProgrammingError as error:
    return render_error("データベースプログラミングエラー", error)
  except Exception as error:
    return render_error("予期せぬエラーが発生しました。", error)

  return render_template("detail.html", rec=rec, fild=fild)

#****************************************************
# アプリケーション実⾏
#****************************************************
if __name__ == "__main__":
  app.debug=True #開発時デバックMODE
  app.run(host="0.0.0.0", port=5000)
