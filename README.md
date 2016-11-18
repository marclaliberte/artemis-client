#Artemis-Client

A dockerized image for the Artemis honeyclient package. Artemis-client
includes the thug honeyclient with hpfeeds for automated URL input
subscriptions.

### Usage

Download latest container

 ```
 docker pull marclaliberte/artemis-client
 ```

Configure the connection and authentication settings for hpfeeds when
starting the Docker container

 ```
 docker run -it -e BROKER_ADDR='example.com' -e BROKER_PORT='20000' -e IDENT='artemis-1' -e SECRET='test' marclaliberte/artemis-client /bin/bash

 ```

Once inside the container, run /opt/artemis/artemis.sh
