from confluent_kafka import Consumer, Producer
from bson.objectid import ObjectId
import json
import sys
import threading
import time

class KafkaController:

    def __init__(self, endpoint, photoDB, metrics):
        self.topicFoto = "foto"
        self.topicTag = "tag"
        self.nFoto = 0
        self.producer = Producer({'bootstrap.servers': endpoint})
        self.consumer = Consumer({'bootstrap.servers': endpoint,
              'group.id': 'group1',
              'enable.auto.commit': 'false',
              # 'auto.offset.reset=earliest' to start reading from the beginning - [latest, earliest, none]
              'auto.offset.reset': 'latest',
              'on_commit': self.commit_completed
              })
        self.consumer.subscribe([self.topicTag])
        thread = threading.Thread(target=self.receiveTag, args=[photoDB, metrics])
        thread.start()

    def commit_completed(self, err, partitions):
        if err:
            print(str(err))
        else:
            print("Committed partition offsets: " + str(partitions))

    def sendForTag(self, photo_id, photo):
        try:
            data = json.dumps({"photo_id": photo_id, "photo_name": photo})
            self.producer.produce(self.topicFoto, key="foto" + str(self.nFoto), value=data)
            self.nFoto += 1
        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %len(self.producer))

    def receiveTag(self, photoDB, metrics):
        try:
            while True:
                msg = self.consumer.poll(timeout=5.0)
                if msg is None:
                    print("Waiting for message or event/error in poll()")
                    #continue
                elif msg.error():
                    print('error: {}'.format(msg.error()))
                else:
                    # Check for Kafka message
                    record_key = msg.key()
                    record_value = msg.value()
                    data = json.loads(record_value)
                    photo_id = data["photo_id"]
                    print(data, file=sys.stderr)
                    photoDB.updatePhotoTags(ObjectId(photo_id), data["photo_tags"])
                    self.consumer.commit(message = msg, asynchronous=True)

                    startTime = photoDB.getPhoto(ObjectId(photo_id))['time']
                    metrics.setTotalTime(time.time()-startTime)
                   
                    print("Consumed record with key {} and value {}".format(record_key, record_value))
        except KeyboardInterrupt:
            pass
        finally:
            self.consumer.close()


            
