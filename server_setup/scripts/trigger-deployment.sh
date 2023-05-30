#!/bin/bash
cd /home/ubuntu/deployment
aws s3 cp s3://dvc-flower-bucket/model.zip ./model.zip --profile duongpd7
sudo docker compose down --rmi all --remove-orphans
yes | unzip ./model.zip
sudo docker compose up -d
echo "Successfully $(date)" >> result.txt
