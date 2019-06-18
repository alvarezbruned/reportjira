FROM python:3.6-slim

RUN apt-get update
RUN \
  pip install requests \
  pyyaml

RUN \
  apt-get install -y libqt5x11extras5 \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /files
COPY requirements.txt /files
COPY __main__.py /files
RUN chmod +x /files/__main__.py
RUN pip3 install -r /files/requirements.txt

COPY reportjira-config.conf /files

ENTRYPOINT python3 /files/__main__.py
