import logging
import traceback
from builtins import range, str
from threading import Event, RLock, Thread
from time import sleep

from external_webpage.instrument_information_collator import InstrumentInformationCollator

scraped_data = {}
scraped_data_lock = RLock()
logger = logging.getLogger('JSON_bourne')

WAIT_BETWEEN_UPDATES = 5
WAIT_BETWEEN_FAILED_UPDATES = 60
RETRIES_BETWEEN_LOGS = 60


class InstrumentScrapper(Thread):
    """
    Thread that continually scrapes data from an instrument's ArchiveEngine.
    """
    _previously_failed = False
    _tries_since_logged = 0

    def wait(self, seconds):
        """
        Wait for a number of seconds but in short waits so can stop thread more quickly
        Args:
            seconds: number of seconds to wait

        Returns:

        """
        for i in range(seconds):
            if self._stop_event.is_set():
                return
            sleep(1)

    def __init__(self, name, host, pv_prefix):
        """
        Initialize.
        Args:
            name: Name of instrument.
            host: Host for the instrument.
            pv_prefix: The pv_prefix of the instrument.
        """
        super(InstrumentScrapper, self).__init__()
        self._host = host
        self._pv_prefix = pv_prefix
        self._name = name
        self._stop_event = Event()

    def is_instrument(self, name, host):
        """
        Is this scrapper for this name and _host
        Args:
            name: name of the instrument
            host: _host of the instrument

        Returns: True is _host and name match; False otherwise

        """
        return self._name == name and self._host == host

    def run(self):
        """
        Function to run continuously to update the scraped data.
        Returns:

        """
        global scraped_data
        web_page_scraper = InstrumentInformationCollator(self._host, self._pv_prefix)
        logger.info("Scrapper started for {}".format(self._name))
        while not self._stop_event.is_set():
            try:
                self._tries_since_logged += 1
                temp_data = web_page_scraper.collate()
                with scraped_data_lock:
                    scraped_data[self._name] = temp_data
                if self._previously_failed:
                    logger.error("Reconnected with " + str(self._name))
                self._previously_failed = False
                self.wait(WAIT_BETWEEN_UPDATES)
            except Exception as e:
                if not self._previously_failed or self._tries_since_logged >= RETRIES_BETWEEN_LOGS:
                    logger.error("Failed to get data from instrument: {0} at {1} error was: {2}{3}".format(
                        self._name, self._host, e, " - Stack (1 line) {stack}:".format(stack=traceback.format_exc())))
                    self._previously_failed = True
                    self._tries_since_logged = 0
                with scraped_data_lock:
                    scraped_data[self._name] = ""
                self.wait(WAIT_BETWEEN_FAILED_UPDATES)

    def stop(self):
        """
        Stop the thread at the next available point
        """
        self._stop_event.set()
