# -*- coding: utf-8 -*-
"""CNN

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18ecxem6DxuHqV1uOHPB08X-cQrosYtid
"""

import numpy as np
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import torchvision
import torchvision.transforms as transforms

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,0.5,0.5),(0.5, 0.5, 0.5)) #Normalizing to [-1 to 1] centred around 0.
    ])

train_data = torchvision.datasets.CIFAR10(root = './data', train = True, transform = transform, download = True)
test_data = torchvision.datasets.CIFAR10(root = './data', train = False, transform = transform, download = True)

train_loader = torch.utils.data.DataLoader(train_data, batch_size = 32, shuffle = True, num_workers = 2)
test_loader = torch.utils.data.DataLoader(test_data, batch_size = 32, shuffle = True, num_workers = 2)

image, label = train_data[0]
image.size()

class_names = ['Plane', 'Car', 'Bird', 'Cat', 'Deer', 'Dog','Frog', 'Horse', 'Ship', 'Truck']

class NeuralNet(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(3,12,5) #channel(input),features,filters(kernel)
        self.pool = nn.MaxPool2d(2,2)  #input, stride | To focusing on the most prominent features while discarding less important information.
        self.conv2 = nn.Conv2d(12,24,5)
        self.fc1 = nn.Linear(24*5*5,120) #No. of inputs*height*width, output
        self.fc2 = nn.Linear(120,84)
        self.fc3 = nn.Linear(84, 10)



    def forward(self, x):
       x = self.pool(F.relu(self.conv1(x)))
       x = self.pool(F.relu(self.conv2(x)))
       x = torch.flatten(x , 1)  #Flattens the feature maps into 1D vector.
       x = F.relu(self.fc1(x))
       x = F.relu(self.fc2(x))
       x = self.fc3(x)
       return x

net = NeuralNet()
loss_function = nn.CrossEntropyLoss() #Used for classification tasks,especially when dealing with categorical data.
optimizer = optim.SGD(net.parameters(), lr = 0.001, momentum = 0.9) #Param = weights and biases, lr = learning rate, Momentum helps the optimizer to accelerate in the direction of the average gradient over multiple iterations.

for epoch in range(30):
    print(f'Training epoch{epoch}....')

    running_loss = 0.0

    for i,data in enumerate(train_loader): #enumerate: Allows you to access both index and corresponding value.

        inputs, labels = data   #Unpacks the data batch into two variables.
        optimizer.zero_grad()   #Sets the gradients of all model parameters to zero.
        outputs = net(inputs)   #Passes the input features through the neural network model net.
        loss = loss_function(outputs, labels)
        loss.backward()         #Computes the gradients of the loss with respect to the model's parameters using backpropagation.
        optimizer.step()        #Updates the model's parameters using the calculated gradients according to the optimization algorithm.

        running_loss += loss.item()  #accumulating the loss across batches

print(f'Loss: {running_loss/ len(train_loader):.4f}')

torch.save(net.state_dict(),'trained_net.pth')  #net.state_dict(): This method retrieves the internal parameter values (weights and biases) of the neural network model stored in net in dictionary form.

net =  NeuralNet()
net.load_state_dict(torch.load('trained_net.pth'))

correct = 0
total = 0

net.eval()

with torch.no_grad():     #Disables SGD
    for data in test_loader:
        images,labels = data  #Extracts the images and corresponding labels from the current batch.
        outputs = net(images)
        _,predicted = torch.max(outputs, 1) #Finds the index of the class with the highest probability for each sample(max_values, max_indices)in the batch but only the index is needed.
        total += labels.size(0) #Represents the batch size and increasing.
        correct += (predicted == labels).sum().item() #item(): Convert the tensor to a scalar for addition.

accuracy = 100*correct/total
print(f'Accuracy:{accuracy}%')

new_transform = transforms.Compose([
    transforms.Resize((32,32)),
    transforms.ToTensor(),
    transforms.Normalize((0.5,0.5,0.5),(0.5,0.5,0.5))
])
def load_image(image_path):
     image = Image.open(image_path)
     image = new_transform(image)
     image = image.unsqueeze(0)
     return image

image_path = ['/ex1.jfif', '/s1.jpg']
images = [load_image (img) for img in image_path]

net.eval()  #Evaluation mode.
with torch.no_grad():
    for image in images:
     output =  net(image)
     _, predicted = torch.max(output, 1) # Underscore (_) is used to discard the first element(maximum value which is highest probability of images)returned by the torch.max function. We only need class.
     print(f'Prediction:{class_names[predicted.item()]}')