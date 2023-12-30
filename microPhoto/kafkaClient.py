from confluent_kafka import Consumer, Producer
import json
import sys
import threading

class KafkaController:
    topicFoto = "foto"
    topicTag = "tag"
    nFoto = 0

    def __init__(self, endpoint, photoDB):
        self.producer = Producer({'bootstrap.servers': endpoint})
        self.consumer = Consumer({'bootstrap.servers': endpoint,
              'group.id': 'group1',
              'enable.auto.commit': 'false',
              # 'auto.offset.reset=earliest' to start reading from the beginning - [latest, earliest, none]
              'auto.offset.reset': 'latest',
              'on_commit': self.commit_completed
              })
        self.consumer.subscribe([self.topicTag])

        thread = threading.Thread(target=self.receiveTag, args=(photoDB,))
        thread.start()

    def commit_completed(err, partitions):
        if err:
            print(str(err))
        else:
            print("Committed partition offsets: " + str(partitions))

    def sendForTag(self, photo_id, photo):
        try:
            data = json.dumps({"photo_id": photo_id, "photo_blob": photo})
            self.producer.produce(self.topicFoto, key="foto" + self.nFoto, value=data)
            self.nFoto += 1
        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %len(self.producer))

    def receiveTag(self, photoDB):
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
                    
                    photoDB.updatePhotoTags(data["photo_id"], data["photo_tags"])

                    self.consumer.commit(asynchronous=True)
                    print("Consumed record with key {} and value {}".format(record_key, record_value))
        except KeyboardInterrupt:
            pass
        finally:
            # Leave group and commit final offsets
            self.client.close()


            
