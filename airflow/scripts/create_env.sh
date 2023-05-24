#!/bin/bash
if [ -d "/opt/airflow/training_env" ]
then
    rm -rf "/opt/airflow/training_env"
fi

mkdir /opt/airflow/training_env
virtualenv /opt/airflow/training_env
git clone https://github.com/phandaiduonghcb/mlops
sed -i 's/include-system-site-packages = false/include-system-site-packages = true/g' /opt/airflow/training_env/pyvenv.cfg
source /opt/airflow/training_env/bin/activate
echo "Install dependencies..."
pip install --quiet -r ./mlops/requirements-dev.txt
cd mlops
echo "Current working dir: $PWD"
dvc pull -r dvc-flower-bucket
ls ./mlops/ml/data/*