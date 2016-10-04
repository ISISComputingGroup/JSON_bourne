from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from threading import Thread
import re
from get_webpage import scrape_webpage
import json
HOST, PORT = '', 60000

EPICS_INSTS = ["NDXDEMO"]

_scraped_data = dict()


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """
        This is called by BaseHTTPRequestHandler every time a client does a GET.
        The response is written to self.wfile
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # Look for the callback
        # JSONP requires a response of the format "name_of_callback(json_string)"
        # e.g. myFunction({ "a": 1, "b": 2})
        result = re.search('/?callback=(\w+)&', self.path)

        # Look for the instrument data
        instruments = re.search('&Instrument=(\w+)&', self.path)

        if len(result.groups()) > 0 and len(instruments.groups()) > 0:
            callback = result.groups()[0]
            inst = instruments.groups()[0]
            ans = "%s(%s)" % (callback, json.dumps(_scraped_data[inst]))
            self.wfile.write(ans)

    def log_message(self, format, *args):
        """ By overriding this method and doing nothing we disable writing to console
         for every client request. Remove this to re-enable """
        return


class Server(Thread):
    def run(self):
        server = HTTPServer(('', PORT), MyHandler)
        server.serve_forever()


class WebScraper(Thread):
    def __init__(self, host):
        super(WebScraper, self).__init__()
        self._host = host

    def run(self):
        while True:
            try:
                temp_data = scrape_webpage(self._host)
                global _scraped_data
                _scraped_data[self._host] = temp_data  # Atomic so no need to lock
            except Exception as e:
                raise Exception("Failed to get data from host: " + self._host)

if __name__ == '__main__':
    try:
        for inst in EPICS_INSTS:
            web_scraper = WebScraper(inst)
            web_scraper.start()

        server = Server()
        server.start()
    except KeyboardInterrupt as e:
        server.join()
        web_scraper.join()
