import sys
import os
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))
print(sys.path)

from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
import mlflow
from mlflow.models.signature import infer_signature
import hyperopt
import pandas as pd
from datetime import datetime
import json
import git
import torch
from torchvision import transforms
import numpy as np
# from torchvision.io import read_image
print("Current working directory: ", )
repo = git.Repo(f'{os.getcwd()}/.git')
sha_commit = repo.head.object.hexsha

from copy import deepcopy
from utils import Params, flatten_dict
from train import run_train_validation
from test import run_test
from datasets import get_valid_transform
import numpy as np
from model import build_model

experiment_name = "classification_runs"
mlflow.set_tracking_uri('file:///opt/airflow/mlruns')
mlflow.set_experiment(experiment_name)

import mlflow

class ClassificationModelWrapper(mlflow.pyfunc.PythonModel):
    def __init__(self, model_path, configs):
        self.model_path = model_path
        self.configs = configs
        self.transform = get_valid_transform(configs.data.image_size, True)
        self.t = transforms.ToPILImage()
        self.model = build_model(
            pretrained=True, 
            fine_tune=True, 
            num_classes=configs.data.num_classes
        ).to(torch.device(configs.train.device))
        self.model.load_state_dict(torch.load(self.model_path)['model_state_dict'])
        self.model.eval()
    def load_context(self, context):
        pass

    def predict(self, context, torch_np_image):
        input = self.t(torch.from_numpy(torch_np_image))
        id = self.model(torch.unsqueeze(self.transform(input), 0)).argmax().item()
        return configs.data.classes[id]

def objective(kwargs):
    # Default config
    temp_config_dict = deepcopy(configs.to_dict())

    # Override default train config and create run folder
    temp_config_dict['train']['learning_rate'] = kwargs[0]['learning_rate']
    temp_config_dict['data']['batch_size'] = kwargs[0]['batch_size']

    result_folder = round(datetime.timestamp(datetime.now()))
    result_path = os.path.join(os.path.dirname(temp_config_dict['train']['result_path']),
                               str(result_folder))
    temp_config_dict['train']['result_path'] = result_path
    temp_config_dict['test']['model_path'] = os.path.join(result_path, 'best.pth')
    temp_config_params = Params(temp_config_dict)
    
    # Write config files to the folder
    if not os.path.exists(temp_config_params.train.result_path):
        os.makedirs(temp_config_params.train.result_path)
        for params, filename in zip([temp_config_params],
                                    ['configs.json']):
            with open(os.path.join(temp_config_params.train.result_path, filename), 'w') as f:
                f.write(json.dumps(params.to_dict()))

    with mlflow.start_run(run_name=str(result_folder)):
        run_id = mlflow.active_run().info.run_id
        print("Current run ID:", run_id)

        model = run_train_validation(temp_config_params)
        test_loss, test_acc = run_test(temp_config_params)
        
        mlflow.set_tag('commit_sha', sha_commit)
        mlflow.log_artifact(os.path.join(result_path,'configs.json'))
        mlflow.log_artifact(os.path.join(result_path,'best.pt'))
        mlflow.log_params(flatten_dict(temp_config_dict))

        model_wrapper = ClassificationModelWrapper(temp_config_params.test.model_path, temp_config_params)

        input = np.random.uniform(0,1,size=(3,temp_config_params.data.image_size,temp_config_params.data.image_size))
        input = input.astype(np.float32)
        output = model_wrapper.predict(None, input)
        signature = infer_signature(input,
                                    output)
        mlflow.pyfunc.log_model(
            python_model=model_wrapper,
            artifact_path="model",
            registered_model_name=f"classification_models",
            # signature=signature,
            pip_requirements=[f'-r {os.getcwd()}/requirements.txt']
        )

        # Get highest sharpe
        # current_experiment=dict(mlflow.get_experiment_by_name(experiment_name))
        # experiment_id=current_experiment['experiment_id']
        # current_experiment['artifact_location']
        # client = mlflow.tracking.MlflowClient()
        # runs = client.search_runs("106567925299128520", "", order_by=["metrics.sharpe DESC"], max_results=1)
        # runs[0].data.metrics['sharpe']
        # runs[0].data.tags['mlflow.log-model.history']
        # json.loads(runs[0].data.tags['mlflow.log-model.history'])[0]['run_id']
        # json.loads(runs[0].data.tags['mlflow.log-model.history'])[0]['artifact_path']

        # runs[0].data.params['path_model_filename']
        # runs[0].data.params['path_result_path']
    return {
        'loss': - test_acc,
        'status': STATUS_OK,

    }

def get_search_space():
    space = {
            'learning_rate': hp.uniform('lr',0.0001,0.001),
            'batch_size': hp.uniformint('batch_size',8,24),
            },
    return space

def get_search_algorithm():
    # return hyperopt.rand.suggest
    return hyperopt.tpe.suggest


def run_hyperparameter_tuning():
    trials = Trials()
    objective_fn = objective
    space = get_search_space()
    search_algo = get_search_algorithm()

    best = fmin(objective_fn,
        space=space,
        algo=search_algo,
        max_evals=1,
        trials=trials)
    
    # trials.trials[0]['misc']['vals']
    return best, trials

configs = Params(f'{os.getcwd()}/ml/configs/configs.json')
start_timestamp = round(datetime.timestamp(datetime.now()))
run_hyperparameter_tuning()
