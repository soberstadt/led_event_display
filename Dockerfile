FROM balenalib/raspberry-pi-python:3.7.2

WORKDIR /usr/src/app

ENV INITSYSTEM on

RUN install_packages gcc make build-essential supervisor

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

CMD ["supervisord", "-n", "-c", "./supervisord.conf"]
