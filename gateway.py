from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

#entrypoint registrazione utente
@app.route("/signup")
def user_signup():
    #Comunicazione diretta gRPC con microUser per ottenere OKAY (TOKEN???)
    pass

#entrypoint login
@app.route("/login")
def user_login():
    #Comunicazione diretta gRPC con microUser per ottenere OKAY (TOKEN???)
    pass


#entrypoint post immagine
@app.route("/post_image")
def post_image():
    #Comunicare con Kafka
    pass

#entrypoint ottenere immagini
@app.route("/get_image")
def get_image():
    #Comunicare con Kafka
    pass
