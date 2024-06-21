#*******************************************************
# PY23 課題01 【開発環境構築】
# CLASS : IH-12A-405(99) NAME : T.Kawashima
#-------------------------------------------------------
#   2024-04-24  NEW
#*******************************************************

from flask import render_template, Flask, request
app = Flask(__name__)

CLASS_TABLE = {
  "IH12A": 5, "IH12B": 5, "PI12": 5, "PW12": 5
}
SUBJECT_TABLE = list(enumerate(("IH22", "NT21", "PY23", "JS22", "DB22", "CS22", "IO21", "FX21")))
RECIEVE_FILEDS = (
  {
    "name": "no",
    "label": "顧客番号"
  }, {
    "name": "name",
    "label": "顧客名"
  }, {
    "name": "custmer_name_kana",
    "label": "顧客名カナ"
  }, {
    "name": "pref",
    "label": "都道府県"
  }, {
    "name": "address_1",
    "label": "住所１"
  }, {
    "name": "address_2",
    "label": "住所２"
  }, {
    "name": "address_1_kana",
    "label": "住所１カナ"
  }, {
    "name": "address_2_kana",
    "label": "住所２仮名"
  }, {
    "name": "phone_number",
    "label": "電話番号"
  }, {
    "name": "mail",
    "label": "メール"
  }, {
    "name": "gender",
    "label": "性　別"
  }
)

def fill_false(_):
  return False

# アンケート送信済み連想配列初期化
submitted = {}
for cls in CLASS_TABLE.keys():
  submitted[cls] = list(map(fill_false, range(CLASS_TABLE[cls])))

#****************************************************
# 結果表示処理 (エンドポイント : '/')
#****************************************************

@app.route("/")
def index():
  return render_template("index.html", RECIEVE_FILEDS = RECIEVE_FILEDS, errors = {}, collected = {})

@app.route("/check", methods=["GET"])
def check():
  collected = {}
  errors = {}
  error = False

  for field in RECIEVE_FILEDS:
    key = field["name"]
    label = field["label"]

    item = request.args.get(key)

    if item is None or item == "":
      error = True
      errors[key] = label + "の値を入力してください"
    else:
      collected[key] = item
    
  print(collected)

  if error:
    return render_template(
      "index.html",
      collected = collected,
      RECIEVE_FILEDS = RECIEVE_FILEDS,
      errors = errors
    )
  else:
    return render_template("check.html", collected = collected, RECIEVE_FILEDS = RECIEVE_FILEDS)


@app.route("/result", methods=["POST"])
def result():
  no = request.form["no"]
  name = request.form["name"]

  return render_template("result.html", cls = cls, no = no, name = name, submitted = submitted, CLASS_TABLE = CLASS_TABLE)

#****************************************************
# アプリケーション実行
#****************************************************
if __name__ == "__main__":
  app.debug=True #開発時デバックMODE
  app.run(host="0.0.0.0", port=5000)
