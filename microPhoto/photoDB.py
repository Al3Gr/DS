import pymongo
from enum import Enum

class PhotoDB:

    def __init__(self, connectionString, username, pwd):
        self.client = pymongo.MongoClient(connectionString, username=username, password=pwd)
        self.db = self.client["dsdb"]
        self.collection = self.db["photos"]

    def addPhoto(self, query):
        query["status"] = PhotoState.UPLOAD.name
        result = self.collection.insert_one(query)
        return result.inserted_id

    def updatePhotoUrl(self, photo_id, url=None):
        _filter = {"_id": photo_id}
        _update = {"$set": {"status": PhotoState.UNTAGGED.name, "url": url}}
        self.collection.update_one(_filter, _update)

    def updatePhotoTags(self, photo_id, tags):
        _filter = {"_id": photo_id}
        _update = {"$set": {"status": PhotoState.TAGGED.name, "tags": tags}}
        self.collection.update_one(_filter, _update)

class PhotoState(Enum):
    UPLOAD = 1
    UNTAGGED = 2
    TAGGED = 3