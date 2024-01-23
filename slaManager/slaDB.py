from pymongo import MongoClient, errors


class SlaDB:

    def __init__(self, connectionString, username, pwd):
        self.client = MongoClient(connectionString, username=username, password=pwd)
        self.db = self.client["dsdb"]
        self.collection = self.db["sla"]

    def create(self, sla):
        try:
            self.collection.insert_one(sla)
            return True
        except errors.DuplicateKeyError:
            return False

