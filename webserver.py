from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from threading import Thread, active_count, RLock
from time import sleep
import re
from get_webpage import scrape_webpage
import json
from logging.handlers import TimedRotatingFileHandler
import logging

logger = logging.getLogger('JSON_bourne')
handler = TimedRotatingFileHandler('log\JSON_bourne.log', when='midnight')
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.setLevel(logging.WARNING)
logger.addHandler(handler)

HOST, PORT = '', 60000

ALL_INSTS = {"MUONFE": "NDEMUONFE"}  # Used for non NDX hosts format of {name: host}

NDX_INSTS = ["DEMO", "LARMOR", "IMAT", "IRIS", "VESUVIO"]

for inst in NDX_INSTS:
    ALL_INSTS[inst] = "NDX" + inst

_scraped_data = dict()
_scraped_data_lock = RLock()


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """
        This is called by BaseHTTPRequestHandler every time a client does a GET.
        The response is written to self.wfile
        """
        try:
            # Look for the callback
            # JSONP requires a response of the format "name_of_callback(json_string)"
            # e.g. myFunction({ "a": 1, "b": 2})
            result = re.search('/?callback=(\w+)&', self.path)

            # Look for the instrument data
            instruments = re.search('&Instrument=(\w+)&', self.path)

            if result is None or instruments is None:
                raise ValueError("No instrument specified")

            if len(result.groups()) != 1 or len(instruments.groups()) != 1:
                raise ValueError("No instrument specified")

            callback = result.groups()[0]
            inst = instruments.groups()[0].upper()

            # Warn level so as to avoid many log messages that come from other modules
            logger.warn("Connected to from " + str(self.client_address) + " looking at " + str(inst))

            with _scraped_data_lock:
                if inst not in _scraped_data.keys():
                    raise ValueError(str(inst) + " not known")
                try:
                    ans = "%s(%s)" % (callback, json.dumps(_scraped_data[inst]))
                except Exception as err:
                    raise ValueError("Unable to convert instrument data to JSON: %s" % err.message)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(ans)
        except ValueError as e:
            self.send_response(400)
            logger.error(e)
        except Exception as e:
            self.send_response(404)
            logger.error(e)

    def log_message(self, format, *args):
        """ By overriding this method and doing nothing we disable writing to console
         for every client request. Remove this to re-enable """
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class WebScraper(Thread):
    _running = True
    _previously_failed = False
    _tries_since_logged = 0

    def wait(self, seconds):
        # Lots of short waits so can stop thread more quickly
        for i in range(seconds):
            if not self._running:
                return
            sleep(1)

    def __init__(self, name, host):
        super(WebScraper, self).__init__()
        self._host = host
        self._name = name

    def run(self):
        while self._running:
            try:
                self._tries_since_logged += 1
                temp_data = scrape_webpage(self._host)
                global _scraped_data
                with _scraped_data_lock:
                    _scraped_data[self._name] = temp_data  # Atomic so no need to lock
                if self._previously_failed:
                    logger.info("Reconnected with " + str(self._name))
                self._previously_failed = False
                self.wait(3)
            except Exception as e:
                if not self._previously_failed or self._tries_since_logged > 60:
                    logger.error("Failed to get data from instrument: " + str(self._name) + " at " + str(self._host) +
                              " error was: " + str(e))
                    self._previously_failed = True
                    self._tries_since_logged = 0
                self.wait(60)

if __name__ == '__main__':
    web_scrapers = []
    for name, host in ALL_INSTS.iteritems():
        web_scraper = WebScraper(name, host)
        web_scraper.start()
        web_scrapers.append(web_scraper)

    server = ThreadedHTTPServer(('', PORT), MyHandler)

    try:
        while True:
            server.serve_forever()
    except KeyboardInterrupt:
        print "Shutting down"
        for w in web_scrapers:
            w._running = False
    while active_count() > 1:
        for w in web_scrapers:
            w.join()
