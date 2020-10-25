FROM python:3.6-slim

RUN apt-get update
RUN \
  pip install requests \
  pyyaml

RUN \
  apt-get install -y libqt5x11extras5 \
  && rm -rf /var/lib/apt/lists/*

COPY files/ /files/
RUN chmod -R +x /files/

COPY reportjira-config.conf /files

ENTRYPOINT /files/reportjira
