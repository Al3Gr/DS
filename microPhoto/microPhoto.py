from enum import Enum
from photoDB import PhotoDB
from flask import Flask, request


class PhotoState(Enum):
    UPLOADING = 1
    NOT_TAGGED = 2
    TAGGED = 3


__db = PhotoDB("DS", "2023")

app = Flask(__name__)


@app.post("/upload")
def upload():
    status = PhotoState.UPLOADING.name
    username = request.form["username"]
    description = request.form["description"]
    #image = request.files
    query = {"username": username, "description": description, "status": status}
    #image['image'].stream.read() // questo è il binary dell'immagine che bisogna mandare tramite grpc
    ## TODO: aggiungere comunicazione con minio tramite gRPC
    photo_id = __db.addPhoto(query)
    return "Test"


@app.get("/get_photo")
def get_photo():
    pass


if __name__ == "main":
    app.run()