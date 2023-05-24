import torch
import argparse
import torch.nn as nn
import torch.optim as optim
from os import path
import os
from pathlib import Path
from tqdm.auto import tqdm
from model import build_model
from datasets import get_datasets, get_data_loaders
from utils import save_model
from torchmetrics import Accuracy
from utils import Params
import mlflow

# Training function.
def train(model, trainloader, optimizer, criterion, acc, device):
    model.train()
    print('Training')
    train_running_loss = 0.0
    all_preds = torch.tensor([], dtype=torch.int64).to(device)
    all_labels = torch.tensor([], dtype=torch.int64).to(device)
    counter = 0
    for i, data in tqdm(enumerate(trainloader), total=len(trainloader)):
        counter += 1
        image, labels = data
        image = image.to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        # Forward pass.
        outputs = model(image)
        # Calculate the loss.
        loss = criterion(outputs, labels)
        train_running_loss += loss.item()
        # Calculate the accuracy.
        _, preds = torch.max(outputs.data, 1)
        all_preds = torch.concat((all_preds, preds))
        all_labels = torch.concat((all_labels, labels))
        # train_running_correct += (preds == labels).sum().item()
        # Backpropagation
        loss.backward()
        # Update the weights.
        optimizer.step()
    
    # Loss and accuracy for the complete epoch.
    epoch_loss = train_running_loss / counter
    epoch_acc = acc(all_labels, all_preds)
    mlflow.log_metrics({"train_loss": epoch_loss,
                        "train_accuracy": epoch_acc.item()})
    return epoch_loss, epoch_acc

# Validation function.
def validate(model,dataset_test, testloader, criterion, acc, log=True, is_test=False, device=torch.device('cpu')):
    model.eval()
    if is_test:
        print('Test!')
    else:
        print('Validation!')
    valid_running_loss = 0.0
    all_preds = torch.tensor([], dtype=torch.int64).to(device)
    all_labels = torch.tensor([], dtype=torch.int64).to(device)
    counter = 0
    
    # Table for logging
    test_table = []
    with torch.no_grad():
        for i, data in tqdm(enumerate(testloader), total=len(testloader)):
            counter += 1
            
            image, labels = data
            image = image.to(device)
            labels = labels.to(device)
            # Forward pass.
            outputs = model(image)
            # Calculate the loss.
            loss = criterion(outputs, labels)
            valid_running_loss += loss.item()
            # Calculate the accuracy.
            _, preds = torch.max(outputs.data, 1)
            all_preds = torch.concat((all_preds, preds))
            all_labels = torch.concat((all_labels, labels))

    epoch_loss = valid_running_loss / counter
    # epoch_acc = 100. * (valid_running_correct / len(testloader.dataset))
    epoch_acc = acc(all_labels, all_preds)
    if is_test:
        mlflow.log_metrics({"test_loss": epoch_loss,
                            "test_accuracy": epoch_acc.item()})
    else:
        mlflow.log_metrics({"val_loss": epoch_loss,
                            "val_accuracy": epoch_acc.item()})
    return epoch_loss, epoch_acc

def run_train_validation(configs: Params):
    if not os.path.exists(configs.train.result_path):
        os.makedirs(configs.train.result_path)
    # Load the training and validation datasets.
    dataset_train, dataset_valid, dataset_test = get_datasets(configs)
    train_loader, valid_loader, _ = get_data_loaders(dataset_train, dataset_valid, dataset_test, configs)
    print(f"[INFO]: Number of training images: {len(dataset_train)}")
    print(f"[INFO]: Number of validation images: {len(dataset_valid)}")
    print(f"[INFO]: Class names: {dataset_train.dataset.classes}\n")
    # Learning_parameters. 
    lr = configs.train.learning_rate
    epochs = configs.train.epochs
    device = configs.train.device
    print(f"Computation device: {device}")
    print(f"Learning rate: {lr}")
    print(f"Epochs to train for: {epochs}\n")
    model = build_model(
        pretrained=True, 
        fine_tune=True, 
        num_classes=len(dataset_train.dataset.classes)
    ).to(device)
    
    # Total parameters and trainable parameters.
    total_params = sum(p.numel() for p in model.parameters())
    print(f"{total_params:,} total parameters.")
    total_trainable_params = sum(
        p.numel() for p in model.parameters() if p.requires_grad)
    print(f"{total_trainable_params:,} training parameters.")
    # Optimizer.
    optimizer = optim.Adam(model.parameters(), lr=lr)
    # Loss function.
    criterion = nn.CrossEntropyLoss()
    # Accuracy:
    acc = Accuracy(task="multiclass", num_classes=len(dataset_train.dataset.classes), top_k=1).to(device)
    # Lists to keep track of losses and accuracies.
    train_loss, valid_loss = [], []
    train_acc, valid_acc = [], []
    # Start the training.
    best_acc = 0.
    for epoch in range(epochs):
        print(f"[INFO]: Epoch {epoch+1} of {epochs}")
        train_epoch_loss, train_epoch_acc = train(model, train_loader, 
                                                optimizer, criterion, acc, device)
        valid_epoch_loss, valid_epoch_acc = validate(model,dataset_valid, valid_loader,  
                                                    criterion, acc, log=False, is_test=False, device=device)
        train_loss.append(train_epoch_loss)
        valid_loss.append(valid_epoch_loss)
        train_acc.append(train_epoch_acc)
        valid_acc.append(valid_epoch_acc)
        if valid_epoch_acc > best_acc:
            name = f'best.pth'
            save_path = path.join(configs.train.result_path, name)
            save_model(
                epochs, 
                model, 
                optimizer, 
                criterion,
                acc, 
                True, 
                save_path)
            best_acc = valid_epoch_acc
        save_model(epochs, 
                   model,
                   optimizer, 
                   criterion,
                   acc,
                   True, 
                   os.path.join(configs.train.result_path, 'last.pth'))
        print(f"Training loss: {train_epoch_loss:.3f}, training acc: {train_epoch_acc:.3f}")
        print(f"Validation loss: {valid_epoch_loss:.3f}, validation acc: {valid_epoch_acc:.3f}")
        print('-'*50)
    print('TRAINING COMPLETE')