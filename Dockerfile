FROM python:3.6

RUN apt-get update
RUN pip install requests
RUN pip install pyyaml

RUN pip3 install reportjira
COPY reportjira-config.conf /usr/local/lib/python3.6/site-packages/reportjira
RUN apt-get install libqt5x11extras5 -y

ENTRYPOINT python3 /usr/local/lib/python3.6/site-packages/reportjira
