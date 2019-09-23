FROM ubuntu:18.04

RUN apt-get -y update &&\
    apt-get -y upgrade &&\
    apt-get -y install python3-pip

RUN pip3 install asyncio &&\
    pip3 install uvloop &&\
    pip3 install urllib3

ADD . .

EXPOSE 80

CMD python3 __main__.py --document_root=./http-test-suite --port=80 --host=0.0.0.0