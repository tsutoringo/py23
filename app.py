from flask import render_template, Flask, request, session, redirect
from datetime import timedelta
import os
import csv

app = Flask(__name__)

app.secret_key = b'PfmpsmMmfPFMmepomfpOMVpPSgreMBsdadRmgp;a:;_eggmrwpomwa'
app.permanent_session_lifetime = timedelta(seconds=10)

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

def need_logged_in(f):
    def _wrapper(*args, **keywords):

        user = get_current_user()

        if user is None:
            return render_template("session_error.html")

        # デコレート対象の関数の実行
        v = f(*args, **keywords)


        return v
    _wrapper.__name__ = f.__name__
    return _wrapper



#****************************************************
# その他util
#****************************************************

def restore_from_field(array, fields):
    result = []
    for (i, ele) in enumerate(array):
        for (index, key) in enumerate(fields.keys()):
            result[i][key] = ele[index]

    return result

#****************************************************
# ログイン画面表示処理 (エンドポイント : '/')
#****************************************************
@app.route("/", methods = [ "GET" ])
def index():
  return render_template("index.html", error = {}, LOGIN_DATA_FIELD = LOGIN_DATA_FIELD)

#****************************************************
# 顧客管理メニュー表示処理 (エンドポイント : '/menu')
#****************************************************
@app.route("/menu", methods = [ "GET" ])
def menu():
    # ログインしてる場合はログインスキップ
    user = get_current_user()
    if user:
        return render_template("menu.html", user = user)

    field, error = get_values_by_field(LOGIN_DATA_FIELD, request.args)

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

@app.route("/page1", methods = [ "GET" ])
@need_logged_in
def page1():
    return render_template("page1.html")

@app.route("/page2", methods = [ "GET" ])
@need_logged_in
def page2():
    return render_template("page2.html")

@app.route("/page3", methods = [ "GET" ])
@need_logged_in
def page3():
    return render_template("page3.html")

@app.route("/logout", methods = [ "GET" ])
def logout():
    set_loggined_user(None)

    return redirect('/')

if __name__ == "__main__":
  app.debug=True
  app.run(host="0.0.0.0", port=5000)
