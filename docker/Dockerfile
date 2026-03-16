FROM debian:latest

RUN apt update -y
RUN apt upgrade -y
RUN apt install python3-venv python3-pip -y

RUN useradd ret
USER ret
WORKDIR /home/ret

COPY requirements .
RUN python3 -m venv .venv
RUN .venv/bin/python -m pip install -r requirements