#!/bin/bash

# Check that the commit is on the 'master' branch
if [[ $(git rev-parse --abbrev-ref HEAD) != 'main' ]]; then
    exit 0
fi

# Get the commit message and search for a keyword that indicates DAG changes
COMMIT_MSG=$(git log -1 --pretty=format:%s)
if [[ "$COMMIT_MSG" != *"Airflow"* ]]; then
    exit 0
fi

# Send a POST request to the Airflow REST API to trigger the DAG
# Remember to use basic_auth in airflow.cfg
curl -X 'POST' \
  --user "airflow:airflow" \
  'http://ec2-3-133-178-16.us-east-2.compute.amazonaws.com:8080/api/v1/dags/tune_dag/dagRuns' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "conf": {},
  "dag_run_id": "'$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")'",
  "logical_date": "'$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")'",
  "note": "Git hook is used to trigger the run"
}'
