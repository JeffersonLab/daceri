FROM ubuntu:latest

COPY ./libs/requirements.txt /work/requirements.txt
COPY ./controller-configs/ /work/.approxeng.input/
COPY ./container/entrypoint.sh /entrypoint.sh

RUN apt update &&\
    apt install -y --no-install-recommends \ 
    python3-pip python-is-python3 python3-venv python3-dev build-essential &&\
    mkdir -p /work/.robot-venv && cd /work &&\
    apt clean &&\
    chmod +x /entrypoint.sh &&\
    python -m venv /work/.robot-venv &&\
    . /work/.robot-venv/bin/activate &&\
    pip install -r requirements.txt &&\
    rm -rf requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
