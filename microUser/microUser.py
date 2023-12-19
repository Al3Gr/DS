import jwt
from flask import Flask, request
from userDB import UserDB

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
    return "OK"


# entrypoint login
@app.post("/login")
def login():
    username = request.form["username"]
    password = request.form["password"]
    query = {"username": username, "password": password}
    result = __db.login(query)
    if not result:
        return "ERROR"
    else:
        t_data = {"username": f"{username}", "valid": True}
        token = jwt.encode(payload=t_data, key="segreto", algorithm="HS256")
        return token


if __name__ == "main":
    app.run()
