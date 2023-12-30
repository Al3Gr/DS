import torch
import os
from PIL import Image
from torchvision import transforms
from torchvision.models import AlexNet_Weights, alexnet
from concurrent.futures import ThreadPoolExecutor
from KafkaController import KafkaController

#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context

def worker(dati):
    print("Thread in esecuzione")
    #salva l'immagine sul disco
    photo_id = dati["photo_id"]
    photo_blob = dati["photo_blob"]
    nomeFile = "photo_"+photo_id+".jpg"

    file = open(nomeFile, "w")
    file.write(photo_blob)
    file.close()

    dictionaryCatProb = inferenza(nomeFile, model=model, preprocess=preprocess)
    
    print("Send response to client")
    kafkaController.produce(photo_id, dictionaryCatProb)

    os.remove(nomeFile)

def inferenza(filename, model, preprocess):
    input_image = Image.open(filename)
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

    try:
        while(True):
            dati = kafkaController.receivePhoto()
            if dati is not None :
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(worker, args=(dati,))
    except KeyboardInterrupt:
        pass
    finally:
        kafkaController.close()
