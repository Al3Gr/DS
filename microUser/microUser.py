import jwt
from flask import Flask, request
from userDB import UserDB
import time

app = Flask(__name__)

__db = UserDB("DS", "2023")


@app.post("/signup")
def signup():
    username = request.form["username"]
    password = request.form["password"]
    query = {"username": username, "password": password}
    result = __db.signup(query)
    if not result:
        return "Error"
    return createToken(username)


# entrypoint login
@app.post("/login")
def login():
    username = request.form["username"]
    password = request.form["password"]
    query = {"username": username, "password": password}
    result = __db.login(query)
    if not result:
        return "ERROR"
    return createToken(username)

def createToken(username):
    t_data = {"username": f"{username}", "expirationTime": time.time() + 3600*2}
    token = jwt.encode(payload=t_data, key="segreto", algorithm="HS256")
    return token

if __name__ == "main":
    app.run()
