#!/usr/bin/env python

from datetime import datetime
import hpfeeds
import gevent
import os
import json
import logging
from urlhandler import UrlHandler
from daemon import runner
from ConfigParser import ConfigParser
from ConfigParser import SafeConfigParser

log = logging.getLogger('Artemis-Client')

class FeedPuller(object):
    def __init__(self, config):

        self.ident = config['hpf_ident']
        self.secret = config['hpf_secret']
        self.port = config['hpf_port']
        self.host = config['hpf_host']
        self.feeds = 'shiva.urls'
        self.last_received = datetime.now()
        self.hpc = None
        self.enabled = True

    def start_listening(self):

        gevent.spawn_later(15, self._activity_checker)
        while self.enabled:
            try:
                self.hpc = hpfeeds.new(self.host, self.port, self.ident, self.secret)

                def on_error(payload):
                    log.critical("Error message from broker: {0}".format(payload))
                    self.hpc.stop()

                def on_message(ident, chan, payload):
                    self.last_received = datetime.now()
                    data = json.loads(str(payload))
                    site_id = data['id']
                    url = data['url'].encode('unicode-escape')
                    self.handler = UrlHandler(url)
                    self.handler.process()

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
                    log.info("No activity for 15 seconds, forcing reconnect")
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
        self.config_file = '/opt/artemis/config.cfg'
        self.thug_config = '/etc/thug/logging.conf'

    def parse_config(self):
        if not os.path.isfile(self.config_file):
            log.critical("Could not find configuration file: {0}".format(self.config_file))
            sys.exit("Could not find configuration file: {0}".format(self.config_file))

        parser = ConfigParser()
        parser.read(self.config_file)

        config = {}

        config['hpf_host'] = parser.get('hpfeeds','host')
        config['hpf_port'] = parser.getint('hpfeeds','port')
        config['hpf_ident'] = parser.get('hpfeeds','ident')
        config['hpf_secret'] = parser.get('hpfeeds','secret')

        return config

    def conf_thug(self,config):
        parser = ConfigParser()
        parser.read(self.thug_config)

        parser.set('hpfeeds','enable', 'True')
        parser.set('hpfeeds','host', config['hpf_host'])
        parser.set('hpfeeds','port', config['hpf_port'])
        parser.set('hpfeeds','ident', config['hpf_ident'])
        parser.set('hpfeeds','secret', config['hpf_secret'])

        with open(self.thug_config, 'w') as configfile:
            parser.write(configfile)
 

    def run(self):
        logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                            filename=self.logfile,
                            level=logging.DEBUG)

        try:
            while True:

                log.info("Artemis Client starting up...")
                log.debug("Parsing Artemis configuration")
                c = self.parse_config()
 
                log.debug("Configuring thug logging settings")
                self.conf_thug(c)

                greenlets = {}
                puller = FeedPuller(c)
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
