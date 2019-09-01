FROM balenalib/raspberry-pi-python:3.7.2

WORKDIR /usr/src/app

ENV INITSYSTEM on

RUN apt-get update
RUN apt-get install gcc make build-essential python-dev git scons swig

RUN git clone https://github.com/jgarff/rpi_ws281x
RUN cd rpi_ws281x/ && scons
RUN cd rpi_ws281x/python && python setup.py build
RUN cd rpi_ws281x/python &&python setup.py install

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

CMD ["python", "run.py"]

