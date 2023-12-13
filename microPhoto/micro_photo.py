from enum import Enum
from photoDB import PhotoDB
from flask import Flask

class PhotoState(Enum):
    UPLOADING = 1
    UPLOADED = 2
    NOT_TAGGED = 3
    TAGGED = 4


__db = PhotoDB()

app = Flask(__name__)

@app.post("/upload_image")
def upload():
    pass


if __name__ == "main":
    app.run()