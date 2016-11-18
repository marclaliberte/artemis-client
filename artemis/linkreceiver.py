#!/usr/bin/env python

from datetime import datetime
import hpfeeds
import gevent
import json
import logging
from urlhandler import UrlHandler

host = '<broker_addr>'
port = <broker_port>
ident = '<ident>'
secret = '<secret>'
channel = 'shiva.urls'
t_id = '<ident>'

logger = logging.getLogger('pyhpfeeds')

class FeedPuller(object):
    def __init__(self, ident, secret, port, host, feeds):

        self.ident = ident
        self.secret = secret
        self.port = port
        self.host = host
        self.feeds = feeds
        self.last_received = datetime.now()
        self.hpc = None
        self.enabled = True

    def handle_url(self,url):
        print "Time: %s -- URL: %s" % (self.last_received, url)

    def start_listening(self):

        gevent.spawn_later(15, self._activity_checker)
        while self.enabled:
            try:
                self.hpc = hpfeeds.new(self.host, self.port, self.ident, self.secret)

                def on_error(payload):
                    print 'Error message from broker: {0}'.format(payload)
                    self.hpc.stop()

                def on_message(ident, chan, payload):
                    self.last_received = datetime.now()
                    data = json.loads(str(payload))
                    site_id = data['id']
                    url = data['url'].encode('unicode-escape')
                    self.handler = UrlHandler(url)
                    self.handler.process()
                    #self.handle_url(url)
                    #print "Time: %s --- Site: %s - URL: %s" % (self.last_received, site_id, url)

                self.hpc.subscribe(self.feeds)
                self.hpc.run(on_message, on_error)
            except Exception as ex:
                print ex
                self.hpc.stop()
            gevent.sleep(5)

    def stop(self):
        self.hpc.stop()
        self.enabled = False

    def _activity_checker(self):
        while self.enabled:
            if self.hpc is not None and self.hpc.connected:
                difference = datetime.now() - self.last_received
                if difference.seconds > 15:
                    print "No activity for 15 seconds, forcing reconnect"
                    self.hpc.stop()
            gevent.sleep(15)

if __name__ == '__main__':

    greenlets = {}

    print "spawning feedpuller"
    puller = FeedPuller(ident, secret, port, host, channel)
    greenlets['hpfeeds-puller'] = gevent.spawn(puller.start_listening)

    try:
        gevent.joinall(greenlets.values())
    except KeyboardInterrupt as err:
        if puller:
            puller.stop()

    gevent.joinall(greenlets.values())
