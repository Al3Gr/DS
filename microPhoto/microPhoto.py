from minio import Minio
import jwt
from photoDB import PhotoDB
from kafkaClient import KafkaController
from flask import Flask, request, make_response

bucketName = "post"
__db = PhotoDB("DS", "2023")
__kafka = KafkaController(__db)
client = Minio (
    "play.min.io",
    access_key="chiaveAccesso",
    secret_key="secretKey",
)
app = Flask(__name__)

def check_token(func):
    def decorator():
        token = request.headers["Authorization"]
        decoded = jwt.decode(token, key= "segreto", algorithms="HS256")
        if decoded["valid"]:
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
        return make_response("", 400)

    query = {"username": username, "description": description}
    photo_id = __db.addPhoto(query)
    client.put_object(
        "asiatrip", photo_id, image.stream, len(blob) 
    )
    __db.updatePhotoUrl(photo_id, photo_id) #sistemare qui il link
    
    __kafka.sendForTag(blob);

    return make_response("", 200)


@app.get("/get_photo")
def get_photo():
    pass

def initMinio():
    if not client.bucket_exists(bucketName):
        client.make_bucket(bucketName)

if __name__ == "__main__":
    app.run()
    initMinio()