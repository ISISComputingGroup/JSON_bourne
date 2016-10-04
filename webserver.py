from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread, active_count
from time import sleep
import re
from get_webpage import scrape_webpage
import json
HOST, PORT = '', 60000

ALL_INSTS = {"MUONFE": "NDEMUONFE"}  # Used for non NDX hosts format of {name: host}

NDX_INSTS = ["DEMO"]

for inst in NDX_INSTS:
    ALL_INSTS[inst] = "NDX" + inst

_scraped_data = dict()


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

            if len(result.groups()) != 1 or len(instruments.groups()) != 1:
                raise ValueError()

            callback = result.groups()[0]
            inst = instruments.groups()[0]

            if inst not in _scraped_data.keys():
                raise ValueError()

            ans = "%s(%s)" % (callback, json.dumps(_scraped_data[inst]))

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(ans)
        except ValueError as e:
            self.send_response(400)
        except Exception as e:
            self.send_response(404)

    def log_message(self, format, *args):
        """ By overriding this method and doing nothing we disable writing to console
         for every client request. Remove this to re-enable """
        return


class WebScraper(Thread):
    _running = True

    def __init__(self, name, host):
        super(WebScraper, self).__init__()
        self._host = host
        self._name = name

    def run(self):
        while self._running:
            try:
                temp_data = scrape_webpage(self._host)
                global _scraped_data
                _scraped_data[self._name] = temp_data  # Atomic so no need to lock

                # Lots of short waits so can stop thread more quickly
                for i in range(3):
                    if not self._running:
                        return
                    sleep(1)
            except Exception as e:
                raise Exception("Failed to get data from instrument: " + str(self._name) + " at " + str(self._host))

if __name__ == '__main__':
    web_scrapers = []
    for name, host in ALL_INSTS.iteritems():
        web_scraper = WebScraper(name, host)
        web_scraper.start()
        web_scrapers.append(web_scraper)

    server = HTTPServer(('', PORT), MyHandler)

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
