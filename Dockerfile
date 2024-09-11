FROM ubuntu:noble

COPY ./libs/requirements.txt /work/requirements.txt
COPY ./controller-configs/ /root/.approxeng.input/

RUN apt update &&\
    apt install -y --no-install-recommends \ 
    python3-pip python-is-python3 python3-venv python3-dev build-essential &&\
    apt clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --break-system-packages -r /work/requirements.txt &&\
    rm -rf requirements.txt

