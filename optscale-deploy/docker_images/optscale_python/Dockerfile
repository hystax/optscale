FROM python:3.9.1
MAINTAINER Hystax
COPY pip.conf /etc

RUN apt-get update \
    && apt-get install -y nano vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && echo "alias ll='ls -laF'" >> ~/.bashrc

# disable vim visual mode
RUN sed -i 's/set mouse=a/set mouse-=a/g' /usr/share/vim/vim81/defaults.vim
