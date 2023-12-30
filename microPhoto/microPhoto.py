from minio import Minio
import jwt
from photoDB import PhotoDB
from kafkaClient import KafkaController
from flask import Flask, request, make_response
import time
import os
import io

bucketName = "post"
__db = PhotoDB(os.environ["mongo_connection"], os.environ["mongo_user"], os.environ["mongo_pwd"])
__kafka = KafkaController(os.environ["kafka_endpoint"], __db)
client = Minio (
    os.environ["minio_endpoint"],
    access_key = os.environ["minio_user"],
    secret_key = os.environ["minio_pwd"],
    secure=False
)
if not client.bucket_exists(bucketName):
    client.make_bucket(bucketName)
app = Flask(__name__)

def check_token(func):
    def decorator():
        token = request.headers["Authorization"]
        decoded = jwt.decode(token, key= "segreto", algorithms="HS256")
        if decoded["expirationTime"] > time.time():
            return func(decoded["username"])
        else:
            return make_response("", 401) #Unauthorized
    return decorator

@app.post("/upload")
@check_token
def upload(username):
    if 'image' not in request.files:
        return make_response("", 400)
    
    description = request.form["description"]
    image = request.files['image'] # questo è come ottenere il file
    blob = image.stream.read() # questo è il binary dell'immagine

    if len(blob) > (1024*1024*2) :
        return make_response("", 400) #troppo grossa l'immagine

    query = {"username": username, "description": description}
    photo_id = __db.addPhoto(query)
    client.put_object(
        "post", str(photo_id), io.BytesIO(blob), len(blob)
    )
    __db.updatePhotoUrl(photo_id, photo_id) #sistemare qui il link
    
    __kafka.sendForTag(str(photo_id), str(blob))

    return make_response("", 200)


@app.get("/get_photo")
def get_photo():
    pass


if __name__ == "__main__":
    app.run()
