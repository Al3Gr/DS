import pymongo


class PhotoDB:

    def __init__(self, username, pwd):
        self.client = pymongo.MongoClient("mongodb://localhost:9081/", username=username, password=pwd)
        self.db = self.client["dsdb"]
        self.collection = self.db["photos"]

    def addPhoto(self, photo):
        result = self.collection.insert_one(photo)
        return result.inserted_id

    def setTagged(self, photo_id, status):
        _filter = {"_id": photo_id}
        _new_status = {"$set": {"status": status}}
        self.collection.update_one(_filter, _new_status)