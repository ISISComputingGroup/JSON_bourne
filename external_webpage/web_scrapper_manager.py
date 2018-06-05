"""
Relation to web scrapper management.
"""
from webserver import InstrumentScrapper


class InstList(object):
    """
    Object that allows the instrument list to be requested from a PV
    """


    def retrieve(self):
        pass


class WebScrapperManager(object):
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
        if inst_list is None:
            self._inst_list = InstList()
        else:
            self._inst_list = inst_list
        self._scrapper_class = scrapper_class
        self.scrappers = []

    def run(self):
        """
        Perform a run of the web scrapper management cycle
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
