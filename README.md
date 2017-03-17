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
 docker run -it marclaliberte/artemis-client /bin/bash

 ```

Inside the container, add hpfeeds settings to /opt/artemis/config.cfg
 ```
 vim /opt/artemis/config.cfg
 ```

Start the client
 ```
 python /opt/artemis/artemis.py start
 ```
