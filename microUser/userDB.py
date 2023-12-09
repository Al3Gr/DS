import pymongo


class userDB:

    def __init__(self):
        client = pymongo.MongoClient("mongodb://localhost:9080/")
        db = client["DS"]
        self.collection = db["users"]

    def signup(self, user):
        self.collection.insert_one(user)

    def login(self, user):
        self.collection.find(user)
