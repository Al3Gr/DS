import pymongo

class UserDB:

    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:9080/")
        self.db = self.client["DS"]
        self.collection = self.db["users"]

    def signup(self, user):
        self.collection.insert_one(user)

    def login(self, user):
        result = self.collection.find_one(user)
        if result:
            return True
        else:
            return False
