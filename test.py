# import requests
# import json
# import numpy as np
import mlflow
import logging
# # Define the input tensor
# input_tensor = np.random.rand(3,512, 512).astype(np.float32).tolist()

# # Define the request headers and data
# url = "http://127.0.0.1:1234/invocations"
# headers = {"Content-Type": "application/json"}
# data = json.dumps({"instances": input_tensor})

# # Send the POST request
# response = requests.post(url, headers=headers, data=data)
# json_response = json.loads(response.content.decode("utf-8"))

# # Print the response status code and content
# print("Response HTTP Status Code: ", response.status_code)
# print("Response Content: ", json_response)


logger = logging.getLogger(__name__)
# set up local logging configuration
mlflow.set_tracking_uri('http://localhost:5000') 
mlflow.set_experiment('my-logging-experiment')
logger.info('this is not uploaded since my run has not started')
with mlflow.start_run(run_name='cc'):
    mlflow.log_param('cc',5)
    logger.info('my experiment is running so the log handler will collect and upload this log')
logger.info('this is not uploaded since my run is over')