import torch
import os
import json
import time
from PIL import Image
from torchvision import transforms
from torchvision.models import AlexNet_Weights, alexnet
#from concurrent.futures import ThreadPoolExecutor
from KafkaController import KafkaController
from io import BytesIO
from minio import Minio
from QoSMetrics import QoSMetrics

#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context


def worker(msg, metrics):
    dati = json.loads(msg.value()) 
    client = Minio(
        os.environ["minio_endpoint"],
        access_key=os.environ["minio_user"],
        secret_key=os.environ["minio_pwd"],
        secure=False
    )
    print("Thread in esecuzione")
    photo_id = dati["photo_id"]
    photo_name = dati["photo_name"]
    try:
        response = client.get_object(os.environ["minio_bucket"], photo_name)
        photo_blob = response.read()
        buffer = BytesIO()
        buffer.write(photo_blob)

        #faccio partire un timer
        t0 = time.time()
        dictionaryCatProb = inferenza(buffer, model=model, preprocess=preprocess)
        #stoppo il timer
        t1 = time.time()
        metrics.setInferenceInfo(list(dictionaryCatProb.keys())[0], t1 - t0)

        print("Send response to client")
        kafkaController.produce(photo_id, dictionaryCatProb) 
        kafkaController.commitMessage(msg)


    finally:
        photo_blob.close()
        photo_blob.release_conn()


def inferenza(buffer, model, preprocess):
    input_image = Image.open(buffer)

    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0)

    if torch.cuda.is_available():
        input_batch = input_batch.to('cuda')
        model.to('cuda')
    with torch.no_grad():
        output = model(input_batch)

    probabilities = torch.nn.functional.softmax(output[0], dim=0)

    dictionaryCatProb = {}
    topK_prob, topK_catid = torch.topk(probabilities, 1)
    for i in range(topK_prob.size(0)):
        dictionaryCatProb[categories[topK_catid[i]]] = topK_prob[i].item()
        print(categories[topK_catid[i]], topK_prob[i].item())

    return dictionaryCatProb


if __name__ == "__main__":
    model = alexnet(weights=AlexNet_Weights.DEFAULT)
    model.eval()


    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                            std=[0.229, 0.224, 0.225]),
    ])

    with open("imagenet_classes.txt", "r") as f:
        categories = [s.strip() for s in f.readlines()]

    kafkaController = KafkaController(os.environ["kafka_endpoint"])

    metrics = QoSMetrics()

    try:
        while True:
            msg = kafkaController.receivePhoto()
            if msg is not None:
                worker(msg, metrics)
    except KeyboardInterrupt:
        pass
    finally:
        kafkaController.close()
