import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms
from torch.utils.data import DataLoader
from data_loader import SkinDiseaseDataset
from tqdm import tqdm

NUM_CLASSES = 50 # Update if you add or remove diseases
BATCH_SIZE = 16
EPOCHS = 10
IMG_SIZE = 224
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Data preparation
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])
train_dataset = SkinDiseaseDataset('data', 'diseases_list.txt', transform)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)

# Model
model = models.resnet18(weights='IMAGENET1K_V1')
model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
model = model.to(DEVICE)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

for epoch in range(EPOCHS):
    model.train()
    loop = tqdm(train_loader, desc=f'Epoch {epoch+1}/{EPOCHS}')
    total_loss = 0
    for imgs, labels in loop:
        imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        loop.set_postfix(loss=loss.item())
    print(f'Epoch {epoch+1}: Loss={total_loss / len(train_loader):.4f}')
    torch.save(model.state_dict(), f'models/resnet18_epoch{epoch+1}.pth')
print('Training complete. Weights saved to models/ directory.')
