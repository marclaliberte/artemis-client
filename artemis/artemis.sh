#!/bin/bash
broker_addr=${BROKER_ADDR}
broker_port=${BROKER_PORT}
client_ident=${IDENT}
client_secret=${SECRET}

sed -i '0,/False/ s/False/True/' /etc/thug/logging.conf
sed -i "s/hpfeeds.honeycloud.net/$broker_addr/g" /etc/thug/logging.conf
sed -i "s/10000/$broker_port/g" /etc/thug/logging.conf
sed -i "s/q6jyo@hp1/$client_ident/g" /etc/thug/logging.conf
sed -i "s/edymvouqpfe1ivud/$client_secret/g" /etc/thug/logging.conf

sed -i "s/<broker_addr>/$broker_addr/g" /opt/artemis/linkreceiver.py
sed -i "s/<broker_port>/$broker_port/g" /opt/artemis/linkreceiver.py
sed -i "s/<ident>/$client_ident/g" /opt/artemis/linkreceiver.py
sed -i "s/<secret>/$client_secret/g" /opt/artemis/linkreceiver.py

