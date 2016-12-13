# This is a Dockerfile for creating an Artemis honeyclient container
# drom an Ubuntu 16.04 image. Tested and known working on Ubuntu 16.04
# Docker installs.
# Artemis includes the Thug (https://github.com/buffer/thug) honeyclient.

FROM ubuntu:16.04
MAINTAINER Marc Laliberte
ENV DEBIAN_FRONTENT noninteractive
ENV V8_HOME /opt/v8/
USER root

# main packages
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
    python-socks \
    build-essential \
    python-dev \
    python-setuptools \
    libboost-python-dev \
    libboost-all-dev \
    libemu-dev \
    subversion \
    curl \
    python-pip \
    libxml2-dev \
    libxslt-dev \
    libfuzzy-dev \
    graphviz \
    libgraphviz-dev \
    git \
    libtool \
    graphviz-dev \
    automake \
    libffi-dev \
    graphviz \
    python-pygraphviz \
    libjpeg8-dev \
    vim \
    autoconf && \
  rm -rf /var/lib/apt/lists/*

# SetupUtils
RUN easy_install -U setuptools

# pip
RUN pip install --upgrade pip
#RUN pip install --upgrade pillow
RUN pip install hpfeeds \
    gevent \
    python-daemon \
    thug

# pyv8
WORKDIR /opt
RUN git clone https://github.com/buffer/pyv8.git && \
  cd pyv8 && \
  python setup.py build && \
  python setup.py install && \
  cd .. && \
  rm -rf pyv8

# artemis setup
RUN mkdir /opt/artemis && \
    mkdir /opt/artemis/logs && \
    mkdir /opt/artemis/pid
COPY artemis/* /opt/artemis/
RUN cp /etc/thug/logging.conf.default /etc/thug/logging.conf

# user setup
RUN mkdir /home/artemis && \
  groupadd artemis && \
  useradd -d /home/artemis -c "Artemis User" -g artemis artemis && \
  chown -R artemis:artemis /home/artemis /opt/artemis /etc/thug


USER artemis
ENV HOME /home/artemis
ENV USER artemis
WORKDIR /opt/artemis
