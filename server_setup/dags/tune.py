from __future__ import annotations
import sys
from pathlib import Path
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonVirtualenvOperator
from datetime import datetime, timedelta
import os


with DAG(dag_id="tune_dag",
         default_args={
             'owner': 'DuongPD7',
             'email': 'phandaiduonghcb@gmail.com',
             'email_on_retry': False,
             'email_on_failure': True,
             'retries': 1,
             'retry_delay': 5,
             'retry_exponential_backoff': False,
             'depends_on_past': True,
         },
         description="A DAG for hyperparameter tuning",
         start_date=datetime(2023,5,15),
         schedule_interval=None,
         catchup=True,
         tags=["mlops"],
         max_active_runs=1,
         ) as dag:

    create_env_task = BashOperator(
        task_id="create_env_task",
        bash_command=" bash -i /opt/airflow/dags/scripts/create_env.sh ",
        retries=1,
    )

    tune_task = BashOperator(
        task_id="tune_task",
        bash_command=" bash -i /opt/airflow/dags/scripts/train.sh ",
        retries=1,
    )

    deploy_task = BashOperator(
        task_id="deploy_task",
        bash_command=" bash -i /opt/airflow/dags/scripts/deploy.sh ",
        retries=1,
    )
    create_env_task >> tune_task >> deploy_task
