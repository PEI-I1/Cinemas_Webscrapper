FROM archlinux:latest
MAINTAINER PEI-i1

RUN pacman -Syu --noconfirm && pacman -S --noconfirm \
    curl \
    git \
    python \
    python-pip \
    redis \
    sudo \
    unzip \
    wget \
    vim

RUN useradd -m -G wheel -s /bin/bash scrapper
RUN echo 'root:root' | chpasswd
RUN echo 'scrapper:scrapper' | chpasswd

USER scrapper

WORKDIR /home/scrapper

RUN git clone https://github.com/PEI-I1/Cinemas_Webscrapper.git
WORKDIR /home/scrapper/Cinemas_Webscrapper

RUN echo 'PATH=$PATH:/home/scrapper/.local/bin' > ../.bashrc

RUN pip install -r requirements.txt --user

WORKDIR /home/scrapper
