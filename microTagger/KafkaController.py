from confluent_kafka import Consumer, Producer
import json
import sys

class KafkaController:

    def __init__(self, endpoint):
        self.topicFoto = "foto"
        self.topicTag = "tag"
        self.producer = Producer({'bootstrap.servers': endpoint})
        self.consumer = Consumer({'bootstrap.servers': endpoint,
              'group.id': 'group1',
              'enable.auto.commit': 'false',
              # 'auto.offset.reset=earliest' to start reading from the beginning - [latest, earliest, none]
              'auto.offset.reset': 'latest',
              'on_commit': self.commit_completed
              })
        self.consumer.subscribe([self.topicFoto])

    def commit_completed(self, err, partitions):
        if err:
            print(str(err))
        else:
            print("Committed partition offsets: " + str(partitions))

    def produce(self, photo_id, photo_tags):
        try:
            data = json.dumps({"photo_id": photo_id, "photo_tags": photo_tags})
            self.producer.produce(self.topicTag, key="foto" + photo_id, value=data)
        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %len(self.producer))

    def receivePhoto(self):
        msg = self.consumer.poll(timeout=5.0)
        if msg is None:
            print("Waiting for message or event/error in poll()")
        elif msg.error():
            print('error: {}'.format(msg.error()))
        else:
            # Check for Kafka message
            record_key = msg.key()
            record_value = msg.value()
            data = json.loads(record_value)  
            return data

    def close(self):
        self.consumer.close()

            
