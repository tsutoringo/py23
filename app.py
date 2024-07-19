from flask import render_template, Flask, request, session, redirect
from datetime import timedelta
import os
import csv

app = Flask(__name__)

app.secret_key = b'PfmpsmMmfPFMmepomfpOMVpPSgreMBsdadRmgp;a:;_eggmrwpomwp'
app.permanent_session_lifetime = timedelta(hours=1)

#****************************************************
# その他フィールド管理
#****************************************************

# フィールドから値を取得してくる
def get_values_by_field(field, values):
    result = {}
    error = {}

    for (key, field) in field.items():
        value = values.get(key)
        label = field["label"]
        if value is None or value == "":
            error[key] = f"{label}が入力されていません"
        else:
            result[key] = value

    return (result, error)

def store2session(prop, datas):
    session[prop] = datas

def get_stored_data(prop):
    return session[prop].copy()

def get_stored_data_and_clear(prop):
    data = get_stored_data(prop)
    session[prop] = None
    return data

# ログインフィールド
LOGIN_DATA_FIELD = {
    "username": {
        "label": "ユーザーID",
        "type": "text"
    },
    "password": {
        "label": "パスワード",
        "type": "password"
    }
}

INPUT_CUSTOMER_FIELD = {
    "customer_no": {
        "label": "顧客番号",
        "type": "text"
    },
    "customer_name": {
        "label": "顧客名",
        "type": "text"
    },
    "customer_name_kana": {
        "label": "顧客名カナ",
        "type": "text"
    },
    "pref": {
        "label": "都道府県",
        "type": "text"
    },
    "address_1": {
        "label": "住所１",
        "type": "text"
    },
    "address_2": {
        "label": "住所２",
        "type": "text"
    },
    "address_1_kana": {
        "label": "住所１カナ",
        "type": "text"
    },
    "address_2_kana": {
        "label": "住所２カナ",
        "type": "text"
    },
    "phonenumber": {
        "label": "電話番号",
        "type": "text"
    },
    "mail": {
        "label": "メール",
        "type": "text"
    },
    "gender": {
        "label": "性別",
        "type": "text"
    }
}

SEARCH_CUSTOMER_FIELD = {
    "customer_no": {
        "label": "顧客番号",
        "type": "text"
    }
}

#****************************************************
# ログイン管理等
#****************************************************

# ユーザー一覧
USERS = {
   "kawa": "ih12a",
   "naka": "ih12b"
}

# ユーザー認証
def auth(username, password):
    expected_password = USERS.get(username)
    # 存在しないユーザーではない かつ 期待するパスワードが期待されるものか
    return (not (expected_password is None)) and expected_password == password

def get_current_user():
    return session.get("loggined_as")

def set_loggined_user(username):
    session["loggined_as"] = username


#****************************************************
# その他util
#****************************************************

def get_csv_filepath():
    cwd = os.path.dirname(__file__)
    return cwd + '/data.txt'

def restore_from_field(array, fields):
    result = []
    for (i, ele) in enumerate(array):
        for (index, key) in enumerate(fields.keys()):
            result[i][key] = ele[index]

    return result

#****************************************************
# ログイン画面表示処理 (エンドポイント : '/')
#****************************************************
@app.route("/")
def index():
  return render_template("index.html", error = {}, LOGIN_DATA_FIELD = LOGIN_DATA_FIELD)

#****************************************************
# 顧客管理メニュー表示処理 (エンドポイント : '/menu')
#****************************************************
@app.route("/menu", methods = [ "POST" ])
def menu():
    # ログインしてる場合はログインスキップ
    user = get_current_user()
    if user:
        return render_template("menu.html", user = user)

    field, error = get_values_by_field(LOGIN_DATA_FIELD, request.form)

    # エラーがある場合
    if len(error.keys()) > 0:
       return render_template("index.html", error = error, LOGIN_DATA_FIELD = LOGIN_DATA_FIELD)

    username = field["username"]
    password = field["password"]

    if auth(username, password):
        set_loggined_user(username)
        return render_template("menu.html", user = get_current_user())
    else:
        return render_template(
            "index.html",
            error = {
                "password": "ユーザーID又はパスワードが違います"
            },
            LOGIN_DATA_FIELD = LOGIN_DATA_FIELD
        )

#****************************************************
# 顧客登録画面表示処理 (エンドポイント : '/inp')
#****************************************************
@app.route("/inp", methods = [ "POST" ])
def inp():
    # ログインユーザー確認
    user = get_current_user()
    if user is None:
        return redirect("/")

    return render_template("input.html", error = {}, user = user, INPUT_CUSTOMER_FIELD = INPUT_CUSTOMER_FIELD, lastdata = get_stored_data("new_customer"))

#****************************************************
# 顧客登録確認画面表示処理 (エンドポイント : '/inpchk')
#****************************************************
@app.route("/inpchk", methods = [ "POST" ])
def inpchk():
    # ログインユーザー確認
    user = get_current_user()
    if user is None:
        return redirect("/")

    field, error = get_values_by_field(INPUT_CUSTOMER_FIELD, request.form)

    store2session("new_customer", field)

    if len(error.keys()) > 0:
       return render_template("input.html", error = error, INPUT_CUSTOMER_FIELD = INPUT_CUSTOMER_FIELD, lastdata = field, user=user)

    return render_template("inpchk.html", INPUT_CUSTOMER_FIELD = INPUT_CUSTOMER_FIELD, new_customer = get_stored_data("new_customer"), user=user)

#****************************************************
# 顧客登録完了画面表示処理 (エンドポイント : '/inpres')
#****************************************************
@app.route("/inpres", methods = [ "POST" ])
def inpres():
    # ログインユーザー確認
    user = get_current_user()
    if user is None:
        return redirect("/")

    # 仕様書にセッションが切れる場合が記載されていないためその場合の考慮はしないものとする
    registerd_customer,_ = get_values_by_field(INPUT_CUSTOMER_FIELD, get_stored_data_and_clear("new_customer"))

    with open(get_csv_filepath(), 'a', encoding='utf8', newline='\n') as file:
        writer = csv.writer(file)

        writer.writerow(
          registerd_customer.values()
        )

    return render_template("inpres.html", registerd_customer = registerd_customer, INPUT_CUSTOMER_FIELD = INPUT_CUSTOMER_FIELD, user = user)

#****************************************************
# 顧客検索機能 (エンドポイント : '/cosinp')
#****************************************************
@app.route("/cosinp", methods = [ "POST" ])
def cosinp():
    user = get_current_user()
    if user is None:
        return redirect("/")

    return render_template("cosinp.html", error = {}, user = user, SEARCH_CUSTOMER_FIELD = SEARCH_CUSTOMER_FIELD)

#****************************************************
# 顧客詳細情報表示処理 (エンドポイント : '/cosres')
#****************************************************
@app.route("/cosres", methods = [ "POST" ])
def cosres():
    # ログインユーザー確認
    user = get_current_user()
    if user is None:
        return redirect("/")

    field, error = get_values_by_field(SEARCH_CUSTOMER_FIELD, request.form)

        # エラーがある場合
    if len(error.keys()) > 0:
       return render_template("cosinp.html", error = error, SEARCH_CUSTOMER_FIELD = SEARCH_CUSTOMER_FIELD, user=user)

    customer_no = field["customer_no"]
    
    registerd_users = []

    with open(get_csv_filepath(), 'r', encoding='utf8', newline='\n') as file:
        reader = csv.reader(file)

        for row in reader:
            if row[0] == customer_no:
                registerd_users.append(row)

    if len(registerd_users) == 0:
       return render_template("cosinp.html", error = {
           "customer_no": f"{customer_no}が存在しません"
       }, SEARCH_CUSTOMER_FIELD = SEARCH_CUSTOMER_FIELD, user=user)

    return render_template("cosres.html", registerd_users = registerd_users, INPUT_CUSTOMER_FIELD = INPUT_CUSTOMER_FIELD, user=user)

#****************************************************
# 顧客情報一覧画面 (エンドポイント : '/cosout')
#****************************************************
@app.route("/cosout", methods = [ "POST" ])
def cosout():
    # ログインユーザー確認
    user = get_current_user()
    if user is None:
        return redirect("/")

    registerd_users = []

    with open(get_csv_filepath(), 'r', encoding='utf8', newline='\n') as file:
        reader = csv.reader(file)

        for row in reader:
            registerd_users.append(row)

    return render_template("cosout.html", registerd_users = registerd_users, user = user, INPUT_CUSTOMER_FIELD = INPUT_CUSTOMER_FIELD)

if __name__ == "__main__":
  app.debug=True
  app.run(host="0.0.0.0", port=5000)
