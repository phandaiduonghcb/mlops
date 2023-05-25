from train import validate
from datasets import get_datasets, get_data_loaders
import torch
import torch.nn as nn
from torchmetrics import Accuracy
from pathlib import Path
from model import build_model
from utils import Params
def run_test(configs: Params):
    dataset_train, dataset_valid, dataset_test = get_datasets(configs)
    print(f"[INFO]: Number of test images: {len(dataset_test)}")
    print(f"[INFO]: Class names: {dataset_test.dataset.classes}\n")
    # Load the training and validation data loaders.
    _, _, test_loader = get_data_loaders(dataset_train,
                                                               dataset_valid,
                                                               dataset_test,
                                                               configs)
    device = configs.train.device
    print(f"Computation device: {device}")
    criterion = nn.CrossEntropyLoss()
    # Accuracy:
    acc = Accuracy(task="multiclass", num_classes=len(dataset_train.dataset.classes), top_k=1).to(device)
    model = build_model(
        pretrained=True, 
        fine_tune=True, 
        num_classes=len(dataset_train.dataset.classes)
    ).to(device)
    model.load_state_dict(torch.load(configs.test.model_path)['model_state_dict'])
    valid_epoch_loss, valid_epoch_acc = validate(model,dataset_test, test_loader,  
                                                    criterion, acc, log=True, is_test=True,
                                                    device=device)
    
    print('Loss: ',valid_epoch_loss)
    print('Accuracy: ',valid_epoch_acc)
    return valid_epoch_loss, valid_epoch_acc

if __name__ == '__main__':
    run_test(Params('/media/duong/DATA/Workspace/AWS/MLops/ml/configs/configs.json'))
