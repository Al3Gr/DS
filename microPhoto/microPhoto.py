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
from QoSMetrics import QoSMetrics

bucketName = os.environ["minio_bucket"]

metrics = QoSMetrics()

__db = PhotoDB(os.environ["mongo_connection"], os.environ["mongo_user"], os.environ["mongo_pwd"])
__kafka = KafkaController(os.environ["kafka_endpoint"], __db, metrics)
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
app.config['MAX_CONTENT_LENGTH'] = 1024*1024*2

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
    
    startTime = time.time()

    description = request.form["description"]
    image = request.files['image'] # questo è come ottenere il file
    blob = image.stream.read() # questo è il binary dell'immagine
    metrics.setImageSize(len(blob))

    photo_id = None
    photo_name = None
    try:
        query = {"username": username, "description": description, "time": startTime}
        photo_id = __db.addPhoto(query)
        photo_name = str(photo_id)+".jpeg"
        client.put_object(
            bucketName, photo_name, io.BytesIO(blob), len(blob)
        )
        __db.updatePhotoUrl(photo_id,  bucketName + "/" + photo_name)
        
        endTime = time.time()
        metrics.setUploadTime(endTime - startTime)

        __kafka.sendForTag(str(photo_id), photo_name)

        return make_response("", 200)
    except Exception:
        if photo_id is not None:
            #compensazione
            __db.deletePhoto(photo_id)
            client.remove_object(bucketName, photo_name)
        return make_response("", 400)


@app.get("/get_photo")
def get_photo():
    username = request.args.get("username", "")
    tag = request.args.get("tag", "")
    skip_s = request.args.get("skip", "")
    query = {}
    if username:
        query["username"] = {"$ne": username}
    if tag:
        nomeField="tags." + tag
        query[nomeField] = { "$exists": True } #sistemare qui
    skip = 0
    if skip_s:
        skip = int(skip_s)
    
    photosInfo = __db.getPhotos(query, skip)
    
    return make_response(dumps(photosInfo), 200)


if __name__ == "__main__":
    app.run()
