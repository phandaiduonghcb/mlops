<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/phandaiduonghcb/mlops">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">MLOPs pipeline for a classification problem</h3>

  <p align="center">
    This repository contains source code, configuration files for setuping a MLOPs pipeline that can be automatically triggered to train and deploy the best model using AWS services.
    <br />
    <a href="https://github.com/phandaiduonghcb/mlops"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/phandaiduonghcb/mlops">View Demo</a>
    ·
    <a href="https://github.com/phandaiduonghcb/mlops/issues">Report Bug</a>
    ·
    <a href="https://github.com/phandaiduonghcb/mlops/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Pytorch][Pytorch]][Pytorch-url]
* [![Mlflow][Mlflow]][Mlflow-url]
* [![Airflow][Airflow]][Airflow-url]
* [![DVC][DVC]][DVC-url]
* [![Docker][Docker]][Docker-url]
* [![Python][Python]][Python-url]
* [![AWS][AWS]][AWS-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Through this guide, I will try to explain how can I use AWS services and some tools to create an MLOPs pipeline that will be triggered to train and deploy everytime the latest commit whose message contains "Airflow" term is pushed.
### Classification problem
A resnet18 neural network will be used for image classification. The dataset will be put into `./ml/data/train`, `./ml/data/valid`, `./ml/data/test`.
The configuration file for training, testing will be put into `./ml/configs`.
I take the [flower dataset](https://public.roboflow.com/classification/flowers_classification/2) as an example for this project.

### Code and Data versioning

DVC is used for data versioning and GIT is used for code versioning. Data cache will be stored in a S3 remote storage.

* Install DVC:
  ```sh
    pip install dvc
    pip install dvc-s3
  ```


* Use DVC to track your data. Remember to setup AWS credentials using `./server_setup/aws_config` and copy all files in that folder to `~/.aws/`
  ```sh
    dvc add ml/data/*
    git add data/*
    git commit -m "Add raw data" # Git tracks the metadata of the dataset
    dvc remote add dvc-flower-bucket s3://dvc-flower-bucket # created s3 bucket for storing data cache
    dvc remote modify dvc-flower-bucket profile duongpd7
    dvc push -r dvc-flower-bucket
  ```

### Setup an EC2 server
Airflow, MLflow will be installed on an EC2 server.
Here are ports that are used in EC2:
- 8080: Airflow
- 1234: Mlflow tracking server
- 4321: deployed endpoint url
- 6000: used to trigger deployment process when there is an model put to s3.
* Create working directory and prepare folders for volume mounting. After creating folders, copy **files** in `server_setup/`:
  ```sh
    mkdir workspace # Store logs, models, artifacts created by Airflow and Mlflow
    mkdir deployment # Build and run deployment docker image
    cd workspace
    mkdir -p ./dags ./logs ./plugins ./config ./mlruns ./training_runs # Have to create manually to avoid permission issue.
  ```
* Now run airflow server and mlflow server using docker compose:
  ```sh
    echo -e "AIRFLOW_UID=$(id -u)" > .env
    docker compose up
  ```

* Setup port 6000 to listening for request sent by from lambda triggered by S3.
  ```sh
    xinetd-deployment-trigger
    apt install xinetd
    # After install xinetd, copy server_setup/scripts/xinetd-deployment-trigger to /etc/xinetd.d/ and modify the its "server" path to server_setup/scripts/trigger-deployment.sh placed on EC2.
    systemctl start xinetd
    systemctl enable xinetd

  ```
### Setup S3 - Lambda for triggering
S3 is configured to trigger lambda function whenever a model.zip file is put into it. The lambda function will send a request to the EC2 server at port 6000 to tell it to rebuild and deploy the model uploaded.
The lambda function should be created from docker image. Source is stored at `deployment/lambda`. The `app.py` file should be modified for the correct url of the EC2.

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Phan Dai Duong - phandaiduonghcb@gmail.com

Project Link: [https://github.com/phandaiduonghcb/mlops](https://github.com/phandaiduonghcb/mlops)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
<!-- ## Acknowledgments

* []()
* []()
* []() -->

<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/phandaiduonghcb/mlops.svg?style=for-the-badge
[contributors-url]: https://github.com/phandaiduonghcb/mlops/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/phandaiduonghcb/mlops.svg?style=for-the-badge
[forks-url]: https://github.com/phandaiduonghcb/mlops/network/members
[stars-shield]: https://img.shields.io/github/stars/phandaiduonghcb/mlops.svg?style=for-the-badge
[stars-url]: https://github.com/phandaiduonghcb/mlops/stargazers
[issues-shield]: https://img.shields.io/github/issues/phandaiduonghcb/mlops.svg?style=for-the-badge
[issues-url]: https://github.com/phandaiduonghcb/mlops/issues
[license-shield]: https://img.shields.io/github/license/phandaiduonghcb/mlops.svg?style=for-the-badge
[license-url]: https://github.com/phandaiduonghcb/mlops/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/phandaiduonghcb
[product-screenshot]: images/screenshot.png
[Pytorch]: https://img.shields.io/badge/Pytorch-000000?style=for-the-badge&logo=Pytorchdotjs&logoColor=white
[Pytorch-url]: https://pytorch.org/
[Mlflow]: https://img.shields.io/badge/Mlflow-20232A?style=for-the-badge&logo=Mlflow&logoColor=61DAFB
[Mlflow-url]: https://mlflow.org/
[Airflow]: https://img.shields.io/badge/Airflow-35495E?style=for-the-badge&logo=Airflowdotjs&logoColor=4FC08D
[Airflow-url]: https://airflow.apache.org/
[DVC]: https://img.shields.io/badge/DVC-DD0031?style=for-the-badge&logo=DVC&logoColor=white
[DVC-url]: https://dvc.org/
[Docker]: https://img.shields.io/badge/Docker-4A4A55?style=for-the-badge&logo=Docker&logoColor=FF3E00
[Docker-url]: https://www.docker.com/
[Python]: https://img.shields.io/badge/Python-FF2D20?style=for-the-badge&logo=Python&logoColor=white
[Python-url]: https://www.python.org/
[AWS]: https://img.shields.io/badge/AWS-563D7C?style=for-the-badge&logo=AWS&logoColor=white
[AWS-url]: https://aws.amazon.com/
