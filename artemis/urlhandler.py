#! /usr/bin/env python
#
# urlhandler.py
#
# This class accepts URLs from the URLReceiver and starts thug
# jobs to investigate
import os,six,subprocess,logging

log = logging.getLogger('Artemis-Client')

class UrlHandler():
    def __init__(self, url):
        self.url = url

    def print_url(self):
        print "URL - %s" % self.url

    def runProcess(self, exe):
        p = subprocess.Popen(exe, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        while(True):
            retcode = p.poll()
            line = p.stdout.readline()
            yield line
            if(retcode is not None):
                break

    def process(self):
        """
        Execute thug to process url
        """

        log.info("Processing: %s" % str(self.url))
        print("Processing: %s" % str(self.url))

        command = ["thug", "-F", "-M", "-v", "-t10",str(self.url)]

        print(command)

        pathname = None

        for line in self.runProcess(command):
            if line.startswith("["):
                six.print_(line, end = " ")

            if line.find("] Saving log analysis at ") >= 0:
                pathname = line.split(" ")[-1].strip()
                log.info("Finished Analysis for: %s" % str(self.url))
                print "Finished Analysis"

