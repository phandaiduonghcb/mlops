FROM apache/airflow:2.6.1-python3.10
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         git zip unzip wget\
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
  && unzip awscliv2.zip \
  && ./aws/install
COPY aws_configure /home/airflow/.aws

ENV CONDA_DIR=/home/airflow/conda
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Linux-x86_64.sh \
    && bash Miniconda3-py310_23.3.1-0-Linux-x86_64.sh -b -p ${CONDA_DIR} \
    && rm -f Miniconda3-py310_23.3.1-0-Linux-x86_64.sh

ENV PATH=$CONDA_DIR/bin:$PATH
RUN conda init bash
RUN conda --version
RUN chmod -R a+rwX /home/airflow/

USER airflow