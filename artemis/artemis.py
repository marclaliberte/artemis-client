#!/usr/bin/env python

from datetime import datetime
import hpfeeds
import os
import json
import logging
from urlhandler import UrlHandler
from daemon import runner
from ConfigParser import ConfigParser
from ConfigParser import SafeConfigParser

log = logging.getLogger('Artemis-Client')

class Artemis(object):
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/opt/artemis/logs/artemis_out.log'
        self.stderr_path = '/opt/artemis/logs/artemis_err.log'
        self.pidfile_path = '/opt/artemis/pid/client.pid'
        self.pidfile_timeout = 5
        self.logfile = '/opt/artemis/logs/client.log'
        self.config_file = '/opt/artemis/config.cfg'
        self.thug_config = '/etc/thug/logging.conf'
        self.feeds = 'shiva.urls'
        self.hpc = None

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

                try:
                    log.info("Connecting to hpfeeds")
                    self.hpc = hpfeeds.new(c['hpf_host'],c['hpf_port'],c['hpf_ident'],c['hpf_secret'])

                    def on_error(payload):
                        log.critical("Error message from broker: {0}".format(payload))
                        self.hpc.stop()

                    def on_message(ident, chan, payload):
                        log.debug("Message received from {0}".format(ident))
                        data = json.loads(str(payload))
                        if 'url' not in data.keys():
                            log.error("No url in payload")
                            return
                        url = data["url"].encode('unicode-escape')
                        self.handler = UrlHandler(url)
                        self.handler.process()

                    self.hpc.subscribe(self.feeds)
                    self.hpc.run(on_message, on_error)

                except Exception as ex:
                    log.critical("Exception in hpfeeds {0}".format(ex))
                    self.hpc.stop()

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
