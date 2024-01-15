import jwt
from flask import Flask, request
from userDB import UserDB
import time
import os

app = Flask(__name__)

__db = UserDB(os.environ["mongo_connection"], os.environ["mongo_user"], os.environ["mongo_pwd"])


@app.post("/signup")
def signup():
    request_data = request.get_json()
    username = request_data["username"]
    password = request_data["password"]
    query = {"username": username, "password": password}
    result = __db.signup(query)
    if not result:
        return "Error"
    return createToken(username)


@app.post("/login")
def login():
    request_data = request.get_json()
    username = request_data["username"]
    password = request_data["password"]
    query = {"username": username, "password": password}
    result = __db.login(query)
    if not result:
        return "ERROR"
    return createToken(username)


def createToken(username):
    t_data = {"username": f"{username}", "expirationTime": time.time() + 3600*2}
    token = jwt.encode(payload=t_data, key=os.environ["token_secret"], algorithm="HS256")
    return token


if __name__ == "main":
    app.run()
