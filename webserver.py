import logging
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from logging.handlers import TimedRotatingFileHandler

from external_webpage.request_handler_utils import get_detailed_state_of_specific_instrument, \
    get_whether_ibex_is_running_on_all_instruments, get_instrument_and_callback
from external_webpage.web_scrapper_manager import WebScrapperManager
from external_webpage.instrument_scapper import _scraped_data, _scraped_data_lock

logger = logging.getLogger('JSON_bourne')
log_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log', 'JSON_bourne.log')
handler = TimedRotatingFileHandler(log_filepath, when='midnight', backupCount=30)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.setLevel(logging.WARNING)
logger.addHandler(handler)

HOST, PORT = '', 60000

ALL_INSTS = {"MUONFE": "NDEMUONFE"}  # Used for non NDX hosts format of {name: host}

NDX_INSTS = ["DEMO", "LARMOR", "IMAT", "IRIS", "VESUVIO", "ALF", "ZOOM", "POLARIS", "HRPD", "MERLIN", "ENGINX",
             "RIKENFE", "EMMA-A", "SANDALS", "GEM", "MAPS"]

for inst in NDX_INSTS:
    ALL_INSTS[inst] = "NDX" + inst


class MyHandler(BaseHTTPRequestHandler):
    """
    Handle for web calls for Json Borne
    """

    def do_GET(self):
        """
        This is called by BaseHTTPRequestHandler every time a client does a GET.
        The response is written to self.wfile
        """
        try:
            instrument, callback = get_instrument_and_callback(self.path)

            # Warn level so as to avoid many log messages that come from other modules
            logger.warn("Connected to from " + str(self.client_address) + " looking at " + str(instrument))

            with _scraped_data_lock:
                if instrument == "ALL":
                    ans = get_whether_ibex_is_running_on_all_instruments(_scraped_data)
                else:
                    ans = get_detailed_state_of_specific_instrument(instrument, _scraped_data)

            response = "{}({})".format(callback, ans)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response)
        except ValueError as e:
            logger.error(e)
            self.send_response(400)
        except Exception as e:
            self.send_response(404)
            logger.error(e)

    def log_message(self, format, *args):
        """ By overriding this method and doing nothing we disable writing to console
         for every client request. Remove this to re-enable """
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


if __name__ == '__main__':
    web_manager = WebScrapperManager()
    web_manager.run()

    server = ThreadedHTTPServer(('', PORT), MyHandler)

    try:
        while True:
            server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")
        web_manager.stop_all()
