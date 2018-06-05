"""
Relation to web scrapper management.
"""
from webserver import InstrumentScrapper


class InstListGetter(object):
    """
    Object that allows the instrument list to be requested from a PV
    """
    pass


class WebScrapperManager(object):
    """
    Manager for the web scrappers that are creating the data for the data web
    It is responsible for starting then and making sure they are running
    """

    def __init__(self, scrapper_class=InstrumentScrapper, inst_list_getter=None):
        """
        Initialiser.
        Args:
            scrapper_class: the class for the Scrappers
            inst_list_getter: the instrument list getter
        """
        if inst_list_getter is None:
            self._inst_list_getter = InstListGetter()
        else:
            self._inst_list_getter = inst_list_getter
        self._scrapper_class = scrapper_class
        self.scrappers = []

    def run(self):
        """
        Perform a run of the web scrapper management cycle
        """
        pass
