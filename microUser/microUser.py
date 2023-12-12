from flask import Flask, request
from userDB import UserDB

app = Flask(__name__)

__db = UserDB()

@app.post("/signup")
def signup():
    username = request.form["username"]
    password = request.form["password"]
    query = {"username": username, "password": password}
    __db.signup(query)
    return "Ok"


# entrypoint login
@app.post("/login")
def login():
    username = request.form["username"]
    password = request.form["password"]
    query = {"username": username, "password": password}
    result = __db.login(query)
    if result:
        return "TOKEN"
    return "ERROR"