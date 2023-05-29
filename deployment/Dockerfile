FROM ubuntu:22.04

RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get install -y --no-install-recommends          wget          curl          nginx          ca-certificates          bzip2          build-essential          cmake          openjdk-8-jdk          git-core          maven     && rm -rf /var/lib/apt/lists/*
RUN apt -y update
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata
RUN apt-get install -y swig libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm     libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
RUN curl https://pyenv.run | bash
ENV PYENV_ROOT="/root/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PATH"
RUN command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
RUN eval "$(pyenv init -)" && eval "$(pyenv virtualenv-init -)"
RUN wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
RUN python3 /tmp/get-pip.py
RUN pip install --no-cache-dir virtualenv mlflow==2.3.2 gevent
# && pyenv install 3.10.6
# RUN pyenv virtualenv 3.10.6 mlflow && pyenv virtualenvs
# RUN pyenv global mlflow
# RUN pip install --no-cache-dir mlflow==2.3.2 gevent

RUN git clone https://github.com/phandaiduonghcb/mlops
RUN echo "export PYTHONPATH=\"\${PYTHONPATH}:/mlops/ml\"" >> ~/.bashrc
ARG dst_model_path
RUN echo $dst_model_path
RUN mkdir -p $(dirname $dst_model_path)
COPY best.pth $dst_model_path
RUN mkdir model
COPY model/ /model/
RUN mlflow models prepare-env -m /model
ENV PYTHONPATH "${PYTHONPATH}:/mlops/ml"

CMD mlflow models serve -m /model --host 0.0.0.0 --port 1234
