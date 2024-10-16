from flask import Response, request, Flask, make_response, render_template
from datetime import datetime
import json


app = Flask(__name__)


@app.route("/", methods = [ "GET" ])
def index():
    return render_template("index.html")

@app.route("/setcookie", methods = [ "POST" ])
def set_cookie():
    expires = int(datetime.now().timestamp()) + 3
    response = make_response(render_template("setcookie.html"))
    username = request.form["username"]
    address = request.form["address"]
    user_info = {'username': username, 'address': address}

    response.set_cookie("user", value=json.dumps(user_info), expires=expires)

    return response

@app.route("/getcookie", methods = [ "GET" ])
def get_cookie():
    user = request.cookies.get('user')
    if user is None:
        return render_template("error.html")
    else:
        user = json.loads(user)
        return render_template("getcookie.html", user=user)



if __name__ == "__main__":
    app.debug=True
    app.run(host="0.0.0.0", port=5000)
