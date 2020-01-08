FROM archlinux:latest
MAINTAINER PEI-i1

RUN pacman -Syu --noconfirm && pacman -S --noconfirm \
    bc \
    curl \
    python \
    python-pip \
    sudo \
    unzip \
    wget \
    vim

RUN useradd -m -G wheel -s /bin/bash scrapper
RUN echo 'root:root' | chpasswd
RUN echo 'scrapper:scrapper' | chpasswd

RUN sed -irs 's/# (%wheel ALL=\(ALL\) ALL)/\1/g' /etc/sudoers

USER scrapper

WORKDIR /home/scrapper

COPY --chown=scrapper . Cinemas_Webscraper
WORKDIR /home/scrapper/Cinemas_Webscraper

ENV PATH="/home/scrapper/.local/bin:${PATH}"

RUN pip install -r requirements.txt --user --no-warn-script-location

CMD ./manage.py makemigrations && \
    ./manage.py migrate && \
    ./manage.py loaddata static/cinemas_fixture.json && \
    (celery -A cinemas_scrapper.celery worker -B -l info &) && \
    ./manage.py runserver 0.0.0.0:5003
