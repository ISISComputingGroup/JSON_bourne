import json
import logging
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from logging.handlers import TimedRotatingFileHandler

from external_webpage.request_handler_utils import get_detailed_state_of_specific_instrument, \
    get_summary_details_of_all_instruments, get_instrument_and_callback
from external_webpage.web_scrapper_manager import WebScrapperManager
from external_webpage.instrument_scapper import scraped_data, scraped_data_lock

logger = logging.getLogger('JSON_bourne')
log_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log', 'JSON_bourne.log')
handler = TimedRotatingFileHandler(log_filepath, when='midnight', backupCount=30)
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.setLevel(logging.INFO)
logger.addHandler(handler)

HOST, PORT = '', 60000

# If the instrument time differs by the webserver time by more than
# TIME_SHIFT_THRESHOLD seconds, then this should be reported web dashboard.
TIME_SHIFT_THRESHOLD = 5 * 3600


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

            with scraped_data_lock:
                if instrument == "ALL":
                    ans = {
                        "error": web_manager.instrument_list_retrieval_errors(),
                        "instruments": get_summary_details_of_all_instruments(scraped_data)}

                else:
                    ans = get_detailed_state_of_specific_instrument(instrument, scraped_data, TIME_SHIFT_THRESHOLD)

            try:
                ans_as_json = str(json.dumps(ans))
            except Exception as err:
                raise ValueError("Unable to convert answer data to JSON: %s" % err.message)

            response = "{}({})".format(callback, ans_as_json)

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
    # It can sometime be useful to define a local instrument list to add/override the instrument list do this here
    # E.g. to add local instrument local_inst_list = {"localhost": "localhost"}
    local_inst_list = {}
    web_manager = WebScrapperManager(local_inst_list=local_inst_list)
    web_manager.start()

    server = ThreadedHTTPServer(('', PORT), MyHandler)

    try:
        while True:
            server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down")
        web_manager.stop()
        web_manager.join()
