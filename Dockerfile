FROM ubuntu:latest
MAINTAINER PEI-i1

RUN apt-get update && apt-get install -y --force-yes \
    curl \
    git \
    python \
    python3-pip \
    redis-server \
    sudo \
    unzip \
    wget \
    vim

RUN useradd --create-home --shell /bin/bash scrapper
RUN echo 'root:root' | chpasswd
RUN echo 'scrapper:scrapper' | chpasswd

USER scrapper

WORKDIR /home/scrapper

RUN git clone https://github.com/PEI-I1/Cinemas_Webscrapper.git
WORKDIR /home/scrapper/Cinemas_Webscrapper

RUN pip3 install -r requirements.txt --user

WORKDIR /home/scrapper
