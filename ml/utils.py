import torch
from model import build_model
import json

def save_model(epochs, model, optimizer, criterion, acc, pretrained, save_path):
    """
    Function to save the trained model to disk.
    """
    torch.save({
                'epoch': epochs,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'acc': acc,
                'loss': criterion,
                }, save_path)
    
def load_model(model_path, pretrained,fine_tune, num_classes,device):
    model = build_model(
        pretrained=pretrained, 
        fine_tune=True, 
        num_classes=len(num_classes)
    ).to(device)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class Params():
    def __init__(self, input):

        if isinstance(input, str):
            with open(input, 'r') as f:
                input_dict = json.load(f)
        elif isinstance(input,dict):
            input_dict = input
        else:
            raise NotImplementedError(f'Input type {type(input)} is not supported!')
        
        for key in input_dict.keys():
            if isinstance(input_dict[key],dict):
                setattr(self, key, Params(input_dict[key]))
            elif isinstance(input_dict[key],(list,str,int,float)):
                setattr(self, key, input_dict[key])
        self._input_dict = input_dict

    def write(self, path):
        with open(path, 'w') as f:
            f.write(json.dumps(self._input_dict))
    
    def to_dict(self):
        return self._input_dict
