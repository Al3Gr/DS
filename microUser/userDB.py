from pymongo import MongoClient, errors


class UserDB:

    def __init__(self, username, pwd):
        self.client = MongoClient("mongodb://userdb:27017/", username=username, password=pwd)
        self.db = self.client["dsdb"]
        self.collection = self.db["users"]

    def signup(self, user):
        try:
            self.collection.insert_one(user)
            return True
        except errors.DuplicateKeyError:
            return False

    def login(self, user):
        result = self.collection.find_one(user)
        if result:
            return True
        else:
            return False
