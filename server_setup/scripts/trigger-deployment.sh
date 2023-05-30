#!/bin/bash
cd /home/ubuntu/deployment
sudo docker compose down --rmi all --remove-orphans
if [ -f "best.pth" ]; then
    sudo rm -rf best.pth .env model
fi
aws s3 cp s3://dvc-flower-bucket/model.zip ./model.zip --profile duongpd7
unzip model.zip
export $(cat .env | xargs)
sudo docker compose up -d
echo "Successfully"
