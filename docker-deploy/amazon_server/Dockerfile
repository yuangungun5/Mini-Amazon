FROM ubuntu:18.04

RUN mkdir /amazon_server
RUN apt-get update && apt-get -y install python3
RUN apt-get update && apt-get -y install python3-pip
RUN python3 -m pip install threadpool
RUN python3 -m pip install google
RUN python3 -m pip install psycopg2-binary
RUN python3 -m pip install protobuf

WORKDIR /amazon_server
ADD . /amazon_server

CMD python3 /amazon_server/server.py