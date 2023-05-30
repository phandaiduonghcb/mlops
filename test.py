import requests
import json
import numpy as np
import mlflow
import logging
from torchvision.io import read_image
# Define the input tensor
image = read_image('/media/duong/DATA/Workspace/AWS/MLops/ml/data/train/daisy/5794835_d15905c7c8_n_jpg.rf.9bd0ab510957d17519330fcf1e755d14.jpg')
input_tensor = image.numpy().astype(np.float32).tolist()

# Define the request headers and data
url = "http://ec2-3-133-178-16.us-east-2.compute.amazonaws.com:4321/invocations"
headers = {"Content-Type": "application/json"}
data = json.dumps({"instances": input_tensor})

# Send the POST request
response = requests.post(url, headers=headers, data=data)
json_response = json.loads(response.content.decode("utf-8"))

# Print the response status code and content
print("Response HTTP Status Code: ", response.status_code)
print("Response Content: ", json_response)

# Log to remote mlflow server
# logger = logging.getLogger(__name__)
# # set up local logging configuration
# mlflow.set_tracking_uri('http://localhost:5000') 
# mlflow.set_experiment('my-logging-experiment')
# logger.info('this is not uploaded since my run has not started')
# with mlflow.start_run(run_name='aa'):
#     mlflow.log_param('aa',5)
#     logger.info('my experiment is running so the log handler will collect and upload this log')
# logger.info('this is not uploaded since my run is over')