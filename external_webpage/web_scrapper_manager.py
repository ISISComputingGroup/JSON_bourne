"""
Relation to web scrapper management.
"""
import json
import logging
import zlib
from threading import Thread, Event
from time import sleep

import six
from CaChannel.util import caget

from external_webpage.instrument_scapper import InstrumentScrapper

logger = logging.getLogger('JSON_bourne')
INST_LIST_PV = "CS:INSTLIST"
TIME_BETWEEN_INSTLIST_REFRESH = 6000


class InstList(object):
    """
    Object that allows the instrument list to be requested from a PV
    """

    def __init__(self):
        """
        Initialise.
        """
        self._cached_list = {}
        self.error_on_retrieve = "Instrument list not yet retrieved"

    def retrieve(self):
        """
        retrieve the instrument list
        Returns: list of instruments with their host names
        """

        inst_list = {}
        try:

            raw = caget(INST_LIST_PV, as_string=True)

        except Exception as ex:
            self.error_on_retrieve = "Instrument list can not be read"
            logger.error("ERROR: Error getting instrument list. {}".format(ex))
            return self._cached_list

        try:
            full_inst_list_string = self._dehex_and_decompress(raw)
        except Exception as ex:
            self.error_on_retrieve = "Instrument list can not decompressed"
            logger.error("ERROR: Error getting instrument list. {}".format(ex))
            return self._cached_list

        try:
            full_inst_list = json.loads(full_inst_list_string)
        except Exception as ex:
            self.error_on_retrieve = "Instrument list is not json"
            logger.error("ERROR: Error getting instrument list. {}".format(ex))
            return self._cached_list

        try:
            for full_inst in full_inst_list:
                inst_list[full_inst["name"]] = full_inst["hostName"]
        except KeyError as ex:
            self.error_on_retrieve = "Instrument list not in correct format"
            logger.error("ERROR: Error getting instrument list. {}".format(ex))
            return self._cached_list

        self._cached_list = inst_list
        self.error_on_retrieve = ""

        return self._cached_list

    def _dehex_and_decompress(self, value):
        """
        Decompress and dehex pv value
        Args:
            value: value to translate

        Returns: dehexed value

        """
        if six.PY2:
            return zlib.decompress(value.decode('hex'))

        try:
            # If it comes as bytes then cast to string
            value = value.decode('utf-8')
        except AttributeError:
            pass

        return zlib.decompress(bytes.fromhex(value)).decode("utf-8")


class WebScrapperManager(Thread):
    """
    Manager for the web scrappers that are creating the data for the data web
    It is responsible for starting then and making sure they are running
    """

    def __init__(self, scrapper_class=InstrumentScrapper, inst_list=None):
        """
        Initialiser.
        Args:
            scrapper_class: the class for the Scrappers
            inst_list: the instrument list getter
        """
        super(WebScrapperManager, self).__init__()
        if inst_list is None:
            self._inst_list = InstList()
        else:
            self._inst_list = inst_list
        self._scrapper_class = scrapper_class
        self.scrappers = []
        self._stop_event = Event()

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

    def run(self):
        """
        Perform a run of the web scrapper management cycle
        """
        while not self._stop_event.is_set():
            inst_list = self._inst_list.retrieve()
            new_scrappers_list = []
            for scrapper in self.scrappers:
                if scrapper.is_alive() and self._is_scrapper_in_inst_list(inst_list, scrapper):
                    new_scrappers_list.append(scrapper)
                else:
                    scrapper.stop()
            self.scrappers = new_scrappers_list

            for name, host in self._scrapper_to_start(inst_list):
                scrapper = self._scrapper_class(name, host)
                scrapper.start()
                self.scrappers.append(scrapper)

            self.wait(TIME_BETWEEN_INSTLIST_REFRESH)
        self._stop_all()

    def _is_scrapper_in_inst_list(self, inst_list, scrapper):
        """
        Check if scapper is in instrument list
        Args:
            inst_list: the instrument list
            scrapper: scrapper to checker

        Returns: True if in; False otherwise

        """
        for name, host in inst_list.items():
            if scrapper.is_instrument(name, host):
                return True
        return False

    def _scrapper_to_start(self, instruments):
        """
        Generator returning scrapper to start, i.e. ones in the instrument list but not in the scrappers list
        Args:
            instruments:

        Returns:

        """
        for name, host in instruments.items():
            for scrapper in self.scrappers:
                if scrapper.is_instrument(name, host):
                    break
            else:
                yield name, host

    def _stop_all(self):
        """
        Stop all scrapper threads.

        """
        for scrapper in self.scrappers:
            scrapper.stop()

        for scrapper in self.scrappers:
            scrapper.join()

    def instrument_list_retrieval_errors(self):
        """
        Returns: Any error produced by retrieving the instrument list; empty string if no errors
        """
        return self._inst_list.error_on_retrieve

    def stop(self):
        """
        Stop the thread at the next available point
        """
        self._stop_event.set()
