import pymongo


class PhotoDB:

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:9081/")
        self.db = self.client["DS"]
        self.collection = self.db["photos"]

    def addPhoto(self):
        pass

    def setTagged(self):
        pass