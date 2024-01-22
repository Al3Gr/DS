from minio import Minio
import jwt
from photoDB import PhotoDB
from kafkaClient import KafkaController
from flask import Flask, request, make_response
import time
import os
import io
import json
from bson.json_util import dumps

bucketName = "post"
__db = PhotoDB(os.environ["mongo_connection"], os.environ["mongo_user"], os.environ["mongo_pwd"])
__kafka = KafkaController(os.environ["kafka_endpoint"], __db)
client = Minio(
    os.environ["minio_endpoint"],
    access_key = os.environ["minio_user"],
    secret_key = os.environ["minio_pwd"],
    secure=False
)
if not client.bucket_exists(bucketName):
    client.make_bucket(bucketName)
    readonlyobject_policy = {
        "Version": "2012-10-17",
        "Statement": [ {
            "Effect": "Allow",
            "Principal": {
                "AWS": ["*"]
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::"+bucketName+"/*"
        }]
    }
    client.set_bucket_policy(bucketName, json.dumps(readonlyobject_policy))
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 153600


def check_token(func):
    def decorator():
        token = request.headers["Authorization"]
        decoded = jwt.decode(token, key=os.environ["token_secret"], algorithms="HS256")
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

    # if len(blob) > (1024*1024*2) :
        # return make_response("", 400) troppo grossa l'immagine

    query = {"username": username, "description": description, "time": time.time()}
    photo_id = __db.addPhoto(query)
    client.put_object(
        bucketName, str(photo_id)+".jpeg", io.BytesIO(blob), len(blob)
    )
    __db.updatePhotoUrl(photo_id,  bucketName + "/" + str(photo_id)) #sistemare qui il link
    
    __kafka.sendForTag(str(photo_id), blob.decode('latin1'))

    return make_response("", 200)


@app.get("/get_photo")
def get_photo():
    request_data = request.get_json()
    query = {}
    if "username" in request_data:
        query["username"] = {"$ne": request_data["username"]}
    if "tag" in request_data:
        nomeField="tags." + request_data["tag"] 
        query[nomeField] = { "$exists": True } #sistemare qui
    skip = 0
    if "skip" in request_data:
        skip = request_data["skip"]
    
    photosInfo = __db.getPhotos(query, skip)
    
    return make_response(dumps(photosInfo), 200)


if __name__ == "__main__":
    app.run()
