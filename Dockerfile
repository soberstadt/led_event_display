FROM balenalib/raspberry-pi-alpine-python:3.7.2

WORKDIR /usr/src/app

ENV INITSYSTEM on

RUN apk add build-base

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

CMD ["python", "run.py"]

