from kafka import KafkaProducer, KafkaConsumer

class KafkaController:
    topicFoto = "foto"
    topicTag = "tag"

    def __init__(self, photoDB):
        self.producer = KafkaProducer(bootstrap_servers='localhost:1234')
        self.consumer = KafkaConsumer(self.topicTag, bootstrap_servers='localhost:1234', auto_commit_enable=True)
        self.receiveTag(photoDB)

    def sendForTag(self, photo):
        self.producer.send(self.topicFoto, photo)

    def receiveTag(self, photoDB):
        for message in self.consumer:
            dati = message.value
            photoDB.updatePhotoTags(dati["photo_id"], dati["photo_tags"])
