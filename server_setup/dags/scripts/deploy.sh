#!/bin/bash
conda activate training_env
conda env list
set -e
whoami
export MLFLOW_TRACKING_URI='http://ec2-3-133-178-16.us-east-2.compute.amazonaws.com:1234/'
EXPERIMENT_NAME='classification_runs'
MLRUNS_FOLDER='/opt/airflow/mlruns/'
NEWEST_ARTIFACT_PATH=$(python << EOF
import mlflow
current_experiment=dict(mlflow.get_experiment_by_name("$EXPERIMENT_NAME"))
experiment_id=current_experiment['experiment_id']
client = mlflow.tracking.MlflowClient()
newest_run = client.search_runs(experiment_id, "", order_by=["start_time DESC"], max_results=1)[0]
print(newest_run.info.artifact_uri.replace("file://", ""))
EOF
)
BEST_ARTIFACT_PATH=$(python << EOF
import mlflow
current_experiment=dict(mlflow.get_experiment_by_name("$EXPERIMENT_NAME"))
experiment_id=current_experiment['experiment_id']
client = mlflow.tracking.MlflowClient()
best_run = client.search_runs(experiment_id, "", order_by=["metrics.test_accuracy DESC"], max_results=1)[0]
print(best_run.info.artifact_uri.replace("file://", ""))
EOF
)

if [[ $BEST_ARTIFACT_PATH != $NEWEST_ARTIFACT_PATH ]]
then
    echo "The newest run is not the best one!"
    exit 0
fi

RUN_ID=$(basename $(dirname $BEST_ARTIFACT_PATH))
EXPERIMENT_ID=$(basename $(dirname $(dirname $BEST_ARTIFACT_PATH)))

REMOTE_MODEL_PATH=$(mlflow runs describe --run-id $RUN_ID |\
                jq '.data.params.test_model_path'
                )
REMOTE_MODEL_PATH=${REMOTE_MODEL_PATH//\"/}

conda deactivate
echo "Compress model artifacts..."
HOST_MODEL_PATH=$MLRUNS_FOLDER/$EXPERIMENT_ID/$RUN_ID/artifacts/model
echo """
HOST_MODEL_PATH=$HOST_MODEL_PATH
RUN_ID=$RUN_ID
EXPERIMENT_ID=$EXPERIMENT_ID
REMOTE_MODEL_PATH=$REMOTE_MODEL_PATH
""" >> .env

cp $REMOTE_MODEL_PATH best.pth
cp -r $HOST_MODEL_PATH model
zip -r model.zip .env model best.pth
aws s3 cp model.zip s3://dvc-flower-bucket --profile duongpd7

# conda env remove -n training_env