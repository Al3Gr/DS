# from flask import Flask, request
#
#
#
# app = Flask(__name__)
#
#
# @app.route("/h<name>")
# def hello_world(name):
#     return f"<p>Hello, World {name}!</p>"
#
#
# @app.route("/test", methods=["GET"]) #testato passaggio di query parameters
# def test():
#     args = request.args
#     return args
#
#
# # entrypoint registrazione
# @app.post("/signup")
# def signup():
#     username = request.form["username"]
#     password = request.form["password"]
#     with grpc.insecure_channel('localhost:20000') as channel:
#         stub = user_pb2_grpc.UserServiceStub(channel)
#         response = stub.UserSignup(user_pb2.User(username=username, password=password))
#     return response.success
#
#
# # entrypoint login
# @app.post("/login")
# def login():
#     username = request.form["username"]
#     password = request.form["password"]
#     with grpc.insecure_channel('localhost:20000') as channel:
#         stub = user_pb2_grpc.UserServiceStub(channel)
#         response = stub.UserLogin(user_pb2.User(username=username, password=password))
#     return response.token
#
#
# # entrypoint post immagine
# @app.route("/post_image")
# def post_image():
#     # Comunicare con Kafka
#     pass
#
#
# # entrypoint ottenere immagini
# @app.route("/get_image")
# def get_image():
#     # Comunicare con Kafka
#     pass
