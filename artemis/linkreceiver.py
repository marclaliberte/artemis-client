#!/usr/bin/env python

from datetime import datetime
import hpfeeds
import gevent
import json
import logging
from urlhandler import UrlHandler
from daemon import runner

host = '<broker_addr>'
port = <broker_port>
ident = '<ident>'
secret = '<secret>'
channel = 'shiva.urls'
t_id = '<ident>'

log = logging.getLogger('Artemis')

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

class Artemis(object):
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/opt/artemis/pid/client.pid'
        self.pidfile_timeout = 5
        self.logfile = '/opt/artemis/logs/client.log'

    def run(self):
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            filename=self.logfile,
                            level=logging.DEBUG)

        try:
            while True:
                log.info("Artemis Client starting up...")
                greenlets = {}
                puller = FeedPuller(ident,secret,port,host,channel)
                greenlets['hpfeeds-puller'] = gevent.spawn(puller.start_listening)

                try:
                    gevent.joinall(greenlets.values())
                except:
                    if puller:
                        puller.stop()

                gevent.joinall(greenlets.values())
        except (SystemExit,KeyboardInterrupt):
            pass
        except:
            log.exception("Exception")
        finally:
            log.info("Artemis Client shutting down...")

if __name__ == '__main__':
    client_runner = runner.DaemonRunner(Artemis())
    client_runner.daemon_context.detach_process=True
    client_runner.do_action()
