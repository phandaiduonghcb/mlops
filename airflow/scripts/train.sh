#!/bin/bash

conda activate training_env
conda env list
cd $HOME/conda/envs/training_env/mlops
python ./ml/hyp_tuning.py
echo "Train successfully!"