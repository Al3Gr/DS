import jwt
from flask import Flask, request, make_response
from userDB import UserDB
import time
import os
from QoSMetrics import QoSMetrics

app = Flask(__name__)

__db = UserDB(os.environ["mongo_connection"], os.environ["mongo_user"], os.environ["mongo_pwd"])
metrics = QoSMetrics()

@app.post("/signup")
def signup():
    request_data = request.get_json()
    username = request_data["username"]
    password = request_data["password"]
    query = {"username": username, "password": password}
    result = __db.signup(query)
    if not result:
        return make_response("Username già usato", 400)
    metrics.userLogged("signup")
    return createToken(username)


@app.post("/login")
def login():
    request_data = request.get_json()
    username = request_data["username"]
    password = request_data["password"]
    query = {"username": username, "password": password}
    result = __db.login(query)
    if not result:
        return make_response("Utente non presente", 400)
    metrics.userLogged("login")
    return createToken(username)


def createToken(username):
    t_data = {"username": f"{username}", "expirationTime": time.time() + 3600*2}
    token = jwt.encode(payload=t_data, key=os.environ["token_secret"], algorithm="HS256")
    return token


if __name__ == "main":
    app.run()
