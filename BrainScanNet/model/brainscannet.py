import os
import torch
import torch.nn as nn
import torch.nn.functional as F  # Faltava isso


def get_device():
    # Verificar se a GPU (CUDA) está disponível
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print("Dispositivo GPU (CUDA) disponível!")
    # Verificar se a XPU (Intel®) está disponível
    elif torch.xpu.is_available():
        device = torch.device("xpu")
        print("Dispositivo XPU disponível!")
    # Se não tiver GPU nem XPU, usar a CPU
    else:
        device = torch.device("cpu")
        print("Nenhuma GPU ou XPU disponível, utilizando CPU.")

    return device


# Definição do modelo BrainScanNet
class BrainScanNet(nn.Module):
    def __init__(self, num_classes=4):
        super(BrainScanNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)

        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.5)

        self.fc1 = nn.Linear(256 * 14 * 14, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.pool(F.relu(self.bn4(self.conv4(x))))
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


def load_model():
    device = get_device()
    model = BrainScanNet(num_classes=4).to(device)

    # Caminho relativo ao diretório atual do script
    model_path = os.path.join(os.path.dirname(__file__), "modelo_baseline.pth")

    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    print("Modelo:\n", model)
    return model
