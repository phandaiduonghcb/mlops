import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Dataset
from pathlib import Path
from PIL import Image
import glob, os
from utils import Params
# from tqdm.auto import tqdm

class MyDataset(Dataset):
    def __init__(self, data_dir, transform) -> None:
        super().__init__()
        self.data_dir = Path(data_dir)
        self.dataset = datasets.ImageFolder(root=self.data_dir, transform=transform)
        self.transform = transform
    
    def __getitem__(self, index):
        return self.dataset[index]
    
    def __len__(self):
        return len(self.dataset)



        
def get_train_transform(img_size, pretrained):
    train_transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        normalize_transform(pretrained)
    ])
    return train_transform
# Validation transforms
def get_valid_transform(img_size, pretrained):
    valid_transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        normalize_transform(pretrained)
    ])
    return valid_transform
# Image normalization transforms.
def normalize_transform(pretrained):
    if pretrained: # Normalization for pre-trained weights.
        normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
            )
    else: # Normalization when training from scratch.
        normalize = transforms.Normalize(
            mean=[0.5, 0.5, 0.5],
            std=[0.5, 0.5, 0.5]
        )
    return normalize


def get_datasets(configs:Params):
    """
    Function to prepare the Datasets.
    :param pretrained: Boolean, True or False.
    Returns the training and validation datasets along 
    with the class names.
    """
    dataset_train = MyDataset(
        configs.data.train_data_path, 
        transform=(get_train_transform(configs.data.image_size, True))
    )
    dataset_val = MyDataset(
        configs.data.valid_data_path, 
        transform=(get_valid_transform(configs.data.image_size, True))
    )
    dataset_test = MyDataset(
        configs.data.test_data_path, 
        transform=(get_valid_transform(configs.data.image_size, True))
    )
    
    return dataset_train, dataset_val, dataset_test
def get_data_loaders(dataset_train, dataset_valid, dataset_test, configs: Params):
    """
    Prepares the training and validation data loaders.
    :param dataset_train: The training dataset.
    :param dataset_valid: The validation dataset.
    Returns the training and validation data loaders.
    """
    train_loader = DataLoader(
        dataset_train, batch_size=configs.data.batch_size, 
        shuffle=True, num_workers=configs.data.num_workers
    )
    valid_loader = DataLoader(
        dataset_valid, batch_size=configs.data.batch_size, 
        shuffle=False, num_workers=configs.data.num_workers
    )
    test_loader = DataLoader(
        dataset_test, batch_size=configs.data.batch_size, 
        shuffle=False, num_workers=configs.data.num_workers
    )
    return train_loader, valid_loader , test_loader

if __name__ == "__main__":
    configs = Params('/media/duong/DATA/Workspace/AWS/MLops/ml/configs/configs.json')
    dataset_train, dataset_valid, dataset_test = get_datasets(configs)
    train_loader, valid_loader, test_loader = get_data_loaders(dataset_train, dataset_valid, dataset_test, configs)
    # for i, data in tqdm(enumerate(train_loader), total=len(train_loader)):
    #     pass
