FROM ubuntu:latest

RUN apt update

RUN apt install python3-pip python-is-python3 python3-venv python3-dev build-essential -y

RUN mkdir /work

RUN cd /work

COPY ./libs/requirements.txt ./requirements.txt
COPY ./controller-configs/ /root/.approxeng.input/

RUN mkdir /work/.robot-venv

RUN python -m venv /work/.robot-venv

RUN . /work/.robot-venv/bin/activate && pip install -r requirements.txt

RUN rm -rf requirements.txt

COPY ./container/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
