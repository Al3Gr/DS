import pymongo


class PhotoDB:

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:9081/")
        self.db = self.client["DS"]
        self.collection = self.db["photos"]

    def addPhoto(self, photo):
        self.collection.insert_one(photo)

    def setTagged(self, id, status):
        _filter = {"_id": id}
        _new_status = {"$set": {"stato": status}}
        self.collection.update_one(_filter, _new_status)