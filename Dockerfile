# This is a Dockerfile for creating an Artemis honeyclient container
# drom an Ubuntu 14.04 image. Tested and known working on Ubuntu 14.04
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
    autoconf && \
  rm -rf /var/lib/apt/lists/*

# SetupUtils
RUN easy_install -U setuptools

# pip
RUN pip install --upgrade pip
#RUN pip install --upgrade pillow
RUN pip install hpfeeds \
    gevent \
    thug

# artemis setup
RUN mkdir /opt/artemis
COPY artemis/* /opt/artemis/
RUN cp /etc/thug/logging.conf.default /etc/thug/logging.conf

# yara
#RUN curl -sSL "https://github.com/plusvic/yara/archive/v3.4.0.tar.gz" | tar -xzC . && \
#  cd yara-3.4.0 && \
#  ./bootstrap.sh && \
#  ./configure && \
#  make && \
#  make install && \
#  cd yara-python/ && \
#  python setup.py build && \
#  python setup.py install && \
#  cd ../.. && \
#  rm -rf yara-3.4.0 && \
#  ldconfig

# ssdeep
#RUN curl -sSL https://github.com/REMnux/docker/raw/master/dependencies/ssdeep-2.13.tar.gz |  tar -xzC .  && \
#  cd ssdeep-2.13 && \
#  ./configure && \
#  make install && \
#  cd .. && \
#  rm -rf ssdeep-2.13 && \
#  BUILD_LIB=1 pip install ssdeep

# user setup
RUN mkdir /home/artemis && \ 
#  useradd -r -g artemis -s /sbin/nologin -c "Artemis User" artemis
  groupadd artemis && \
  useradd -d /home/artemis -c "Artemis User" -g artemis artemis && \
  chown -R artemis:artemis /home/artemis /opt/artemis /etc/thug


# pyv8
WORKDIR /opt
RUN git clone https://github.com/buffer/pyv8.git && \
  cd pyv8 && \
  python setup.py build && \
  python setup.py install && \
  cd .. && \
  rm -rf pyv8

# thug
#RUN git clone https://github.com/marclaliberte/thug.git && \
#  chmod a+x thug/src/thug.py && \
#  mkdir thug/logs && \
#  mkdir thug/files && \
#  cp thug/src/Logging/logging.conf.default thug/src/Logging/logging.conf && \
#  chown -R artemis:artemis /opt/thug

# artemis setup
#RUN mkdir /opt/artemis
#COPY artemis/* /opt/artemis/

USER artemis
ENV HOME /home/artemis
ENV USER artemis
WORKDIR /opt/artemis
#ENTRYPOINT ["/opt/thug/tools/artemis/artemis.sh"]
