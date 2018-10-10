"""
Relation to web scrapper management.
"""
import json
import logging
import zlib
from threading import Thread, Event
from time import sleep

import six
from CaChannel import CaChannelException
from CaChannel.util import caget

from external_webpage.instrument_scapper import InstrumentScrapper

# logger for the class
logger = logging.getLogger('JSON_bourne')

# PV that contains the instrument list
INST_LIST_PV = "CS:INSTLIST"

# Time between the refresh of servers from the inst list (10 minutes)
TIME_BETWEEN_INSTLIST_REFRESH = 600


class InstList(object):
    """
    Object that allows the instrument list to be requested from a PV
    """
    INSTRUMENT_LIST_CAN_NOT_BE_READ = "Instrument list can not be read"
    INSTRUMENT_LIST_NOT_DECOMPRESSED = "Instrument list can not decompressed"
    INSTRUMENT_LIST_NOT_JSON = "Instrument list is not json"
    INSTRUMENT_LIST_NOT_CORRECT_FORMAT = "Instrument list not in correct format"

    def __init__(self, caget_fn=caget, local_inst_list=None):
        """
        Initialise.
        Args:
            caget_fn: function to perform a caget
            local_inst_list: local instrument list to override/add entries to the one from instrument list pv
        """
        self.error_on_retrieve = "Instrument list not yet retrieved"
        self._caget_fn = caget_fn
        if local_inst_list is None:
            self._local_inst_list = {}
        else:
            self._local_inst_list = local_inst_list
        self._cached_list = self._local_inst_list

    def retrieve(self):
        """
        retrieve the instrument list
        Returns: list of instruments with their host names
        """

        inst_list = {}
        try:

            raw = self._caget_fn(INST_LIST_PV, as_string=True)

        except CaChannelException as ex:

            self.error_on_retrieve = InstList.INSTRUMENT_LIST_CAN_NOT_BE_READ
            logger.error("ERROR: Error getting instrument list. {}".format(ex))
            return self._cached_list

        try:
            full_inst_list_string = self._dehex_and_decompress(raw)
        except Exception as ex:

            self.error_on_retrieve = InstList.INSTRUMENT_LIST_NOT_DECOMPRESSED
            logger.error("ERROR: Error getting instrument list. {}".format(ex))
            return self._cached_list

        try:
            full_inst_list = json.loads(full_inst_list_string)
        except Exception as ex:

            self.error_on_retrieve = InstList.INSTRUMENT_LIST_NOT_JSON
            logger.error("ERROR: Error getting instrument list. {}".format(ex))
            return self._cached_list

        try:
            for full_inst in full_inst_list:
                inst_list[full_inst["name"]] = full_inst["hostName"]
        except (KeyError, TypeError) as ex:

            self.error_on_retrieve = InstList.INSTRUMENT_LIST_NOT_CORRECT_FORMAT
            logger.error("ERROR: Error getting instrument list. {}".format(ex))
            return self._cached_list

        self._cached_list = inst_list
        self._cached_list.update(self._local_inst_list)
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

    def __init__(self, scrapper_class=InstrumentScrapper, inst_list=None, local_inst_list=None):
        """
        Initialiser.
        Args:
            scrapper_class: the class for the Scrappers
            inst_list: the instrument list getter
            local_inst_list: a local instrument list to add to global instrument list
        """
        super(WebScrapperManager, self).__init__()
        if inst_list is None:
            self._inst_list = InstList(local_inst_list=local_inst_list)
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
            self.maintain_scrapper_list()
            self.wait(TIME_BETWEEN_INSTLIST_REFRESH)
        self.stop_all()

    def maintain_scrapper_list(self):
        """
        Maintain the scrapper list by starting any instrument scrapper on the list and stopping those not on the list
        """
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

    def stop_all(self):
        """
        Stop all scrapper threads.

        """
        for scrapper in self.scrappers:
            scrapper.stop()

        print("   Waiting for scrappers to stop ...")
        for scrapper in self.scrappers:
            scrapper.join()
        print("   ... finished")

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
