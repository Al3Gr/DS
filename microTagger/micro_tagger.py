import torch
import os
import random
from PIL import Image
from torchvision import transforms
from torchvision.models import AlexNet_Weights, alexnet

#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context


model = alexnet(weights=AlexNet_Weights.DEFAULT)
model.eval()

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


def session():
    seed = random.randint(0, 100)
    input_image = Image.open(f"server_image_{seed}.jpeg")
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0)

    if torch.cuda.is_available():
        input_batch = input_batch.to('cuda')
        model.to('cuda')
    with torch.no_grad():
        output = model(input_batch)

    probabilities = torch.nn.functional.softmax(output[0], dim=0)

    with open("imagenet_classes.txt", "r") as f:
        categories = [s.strip() for s in f.readlines()]

    top5_prob, top5_catid = torch.topk(probabilities, 1)
    for i in range(top5_prob.size(0)):
        print(categories[top5_catid[i]], top5_prob[i].item())

    print("Send response to client")
    os.remove(f"server_image_{seed}.jpeg")


