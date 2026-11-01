$script = @"
#!/usr/bin/env python3
'''Train plant disease classification model using PlantVillage dataset.'''

import os
import sys
from pathlib import Path
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from tqdm import tqdm

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / 'data' / 'raw' / 'plant_disease'
MODEL_DIR = ROOT / 'models'
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def find_dataset_dir():
    candidates = [
        DATA_DIR / 'plantvillage' / 'plantvillage-dataset' / 'plantvillage dataset' / 'color',
        DATA_DIR / 'plantvillage' / 'PlantVillage',
        DATA_DIR / 'plantdisease_alt' / 'PlantVillage' / 'PlantVillage',
        DATA_DIR / 'plantvillage',
    ]
    for c in candidates:
        if c.exists() and any(c.iterdir()):
            subdirs = [d for d in c.iterdir() if d.is_dir()]
            if len(subdirs) > 1:
                return c
    for root, dirs, files in os.walk(DATA_DIR):
        if any('___' in d for d in dirs):
            return Path(root)
    return None


def main():
    print('=' * 60)
    print('Plant Disease Classification Training')
    print('=' * 60)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device}')

    data_dir = find_dataset_dir()
    if not data_dir:
        print('ERROR: Dataset not found')
        sys.exit(1)
    print(f'Dataset: {data_dir}')

    transform_train = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    transform_val = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    full_dataset = datasets.ImageFolder(str(data_dir), transform=transform_train)
    print(f'Classes: {len(full_dataset.classes)}')
    print(f'Total images: {len(full_dataset)}')

    with open(MODEL_DIR / 'disease_classes.txt', 'w') as f:
        for c in full_dataset.classes:
            f.write(c + '\n')

    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(full_dataset, [train_size, val_size])
    val_dataset.dataset.transform = transform_val

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=0)

    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, len(full_dataset.classes))
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=10)

    best_acc = 0.0
    epochs = 10

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        pbar = tqdm(train_loader, desc=f'Epoch {epoch+1}/{epochs}')
        for inputs, labels in pbar:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
            pbar.set_postfix({'loss': running_loss/len(pbar)})

        scheduler.step()

        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        acc = 100 * correct / total
        print(f'Epoch {epoch+1} Val Acc: {acc:.2f}%')

        if acc > best_acc:
            best_acc = acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'classes': full_dataset.classes,
                'acc': acc,
            }, MODEL_DIR / 'disease_classifier.pth')
            print(f'Saved best model with acc {acc:.2f}%')

    print('=' * 60)
    print(f'Training complete. Best val acc: {best_acc:.2f}%')
    print('=' * 60)


if __name__ == '__main__':
    main()
"@
Set-Content -Path "C:\Users\ABIR\OneDrive\Desktop\hacathon\KrishiMitra-AI\scripts\train_disease_model.py" -Value $script -Encoding UTF8
Write-Host "done"
