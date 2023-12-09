import grpc
import user_pb2
import user_pb2_grpc
from flask import Flask, request

app = Flask(__name__)


@app.route("/h<name>")
def hello_world(name):
    return f"<p>Hello, World {name}!</p>"


@app.route("/test", methods=["GET"]) #testato passaggio di query parameters
def test():
    args = request.args
    return args


# entrypoint registrazione utente
@app.post("/signup")
def signup():
    username = request.form["username"]
    password = request.form["password"]
    print(f"{username}:{password}")
    # Comunicazione diretta gRPC con microUser per ottenere OKAY (TOKEN???)
    return "Signup"


# entrypoint login
@app.post("/login")
def login():
    username = request.form["username"]
    password = request.form["password"]
    print(f"{username}:{password}")
    # Comunicazione diretta gRPC con microUser per ottenere OKAY (TOKEN???)
    return "Login"


# entrypoint post immagine
@app.route("/post_image")
def post_image():
    # Comunicare con Kafka
    pass


# entrypoint ottenere immagini
@app.route("/get_image")
def get_image():
    # Comunicare con Kafka
    pass
