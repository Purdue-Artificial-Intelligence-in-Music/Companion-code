import torch
from torch import nn
from torch.nn import functional as F

class CNNAudioModel(nn.Module):
    '''
    CNN for audio spectrogram as defined in https://arxiv.org/pdf/1807.06391 
    (see Table 1 on page 4)
    '''
    def __init__(self, input_shape: torch.Tensor = torch.Tensor([1, 78, 40])):
        super(CNNAudioModel, self).__init__()
        out_width1 = ((input_shape[2] + 2 - 3) // 1) + 1
        out_height1 = ((input_shape[1] + 2 - 3) // 1) + 1

        out_width2 = ((out_width1 + 2 - 3) // 1) + 1
        out_height2 = ((out_height1 + 2 - 3) // 1) + 1

        out_width3 = ((out_width2 + 2 - 3) // 2) + 1
        out_height3 = ((out_height2 + 2 - 3) // 2) + 1

        out_width4 = ((out_width3 + 2 - 3) // 1) + 1
        out_height4 = ((out_height3 + 2 - 3) // 1) + 1

        out_width5 = ((out_width4 + 2 - 3) // 2) + 1
        out_height5 = ((out_height4 + 2 - 3) // 2) + 1

        out_width6 = ((out_width5 + 2 - 3) // 2) + 1
        out_height6 = ((out_height5 + 2 - 3) // 2) + 1

        out_width7 = ((out_width6 + 2 - 3) // 1) + 1
        out_height7 = ((out_height6 + 2 - 3) // 1) + 1

        out_width8 = ((out_width7 + 2 - 1) // 1) + 1
        out_height8 = ((out_height7 + 2 - 1) // 1) + 1

        self.conv1 = nn.Conv2d(input_shape[0], 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1)
        self.conv4 = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1)
        self.conv5 = nn.Conv2d(64, 64, kernel_size=3, stride=2, padding=1)
        self.conv6 = nn.Conv2d(64, 96, kernel_size=3, stride=2, padding=1)
        self.conv7 = nn.Conv2d(96, 96, kernel_size=3, stride=1, padding=1)  
        self.conv8 = nn.Conv2d(96, 96, kernel_size=1, stride=1, padding=1)
        self.dropout = nn.Dropout(0.2)
        self.fc1 = nn.Linear(out_width8 * out_height8 * self.conv8.out_channels, 512)

    def forward(self, x: torch.Tensor):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = self.dropout(x)
        x = F.relu(self.conv5(x))
        x = F.relu(self.conv6(x))
        x = F.relu(self.conv7(x))
        x = F.relu(self.conv8(x))
        x = self.dropout(x)
        x = x.flatten()
        x = F.relu(self.fc1(x))
        return x

class CNNScoreModel(nn.Module):
    '''
    CNN for sheet music image as defined in https://arxiv.org/pdf/1807.06391 
    (see Table 1 on page 4)
    '''
    def __init__(self, input_shape: torch.Tensor = torch.Tensor([1, 80, 256])):
        super(CNNScoreModel, self).__init__()
        out_width1 = ((input_shape[2] + 2 - 5) // 2) + 1
        out_height1 = ((input_shape[1] + 2 - 5) // 1) + 1

        out_width2 = ((out_width1 + 2 - 3) // 1) + 1
        out_height2 = ((out_height1 + 2 - 3) // 1) + 1

        out_width3 = ((out_width2 + 2 - 3) // 2) + 1
        out_height3 = ((out_height2 + 2 - 3) // 2) + 1

        out_width4 = ((out_width3 + 2 - 3) // 1) + 1
        out_height4 = ((out_height3 + 2 - 3) // 1) + 1

        out_width5 = ((out_width4 + 2 - 3) // 2) + 1
        out_height5 = ((out_height4 + 2 - 3) // 2) + 1

        out_width6 = ((out_width5 + 2 - 3) // 2) + 1
        out_height6 = ((out_height5 + 2 - 3) // 2) + 1

        out_width7 = ((out_width6 + 2 - 3) // 2) + 1
        out_height7 = ((out_height6 + 2 - 3) // 2) + 1

        out_width8 = ((out_width7 + 2 - 1) // 1) + 1
        out_height8 = ((out_height7 + 2 - 1) // 1) + 1

        self.conv1 = nn.Conv2d(input_shape[0], 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1)
        self.conv4 = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1)
        self.conv5 = nn.Conv2d(64, 64, kernel_size=3, stride=2, padding=1)
        self.conv6 = nn.Conv2d(64, 64, kernel_size=3, stride=2, padding=1)
        self.conv7 = nn.Conv2d(64, 96, kernel_size=3, stride=1, padding=1)  
        self.conv8 = nn.Conv2d(96, 96, kernel_size=1, stride=1, padding=1)
        self.dropout = nn.Dropout(0.2)
        self.fc1 = nn.Linear(out_width8 * out_height8 * self.conv8.out_channels, 512)

    def forward(self, x: torch.Tensor):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = self.dropout(x)
        x = F.relu(self.conv5(x))
        x = F.relu(self.conv6(x))
        x = self.dropout(x)
        x = F.relu(self.conv7(x))
        x = F.relu(self.conv8(x))
        x = self.dropout(x)
        x = x.flatten()
        x = F.relu(self.fc1(x))
        return x

class CombinedScoreAudioModel(nn.Module):
    def __init__(self, input_shape: torch.Tensor):
        super(CombinedScoreAudioModel, self).__init__()
        self.fc1 = nn.Linear(input_shape[0], 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 3)
        self.fc4 = nn.Linear(512, 512)
        self.fc5 = nn.Linear(512, 1)
        self.dropout = nn.Dropout(0.2)

    def forward(self, x: torch.Tensor):
        x = F.relu(self.fc1(x))
        x1 = F.relu(self.fc2(x))
        x1 = self.dropout(x1)
        x1 = self.fc3(x1)
        x1 = F.softmax(x1)

        x2 = F.relu(self.fc4(x))
        x2 = self.dropout(x2)
        x2 = self.fc5(x2)

        return x1, x2

