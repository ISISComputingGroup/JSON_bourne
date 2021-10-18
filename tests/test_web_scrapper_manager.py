from builtins import object
import os
import sys
from hamcrest import *
import unittest

from mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from external_webpage.web_scrapper_manager import WebScrapperManager


class MockWebScrapper(object):
    def __init__(self, name, host, pv_prefix):
        """
        Initialize.
        Args:
            name: Name of instrument.
            host: Host for the instrument.
            pv_prefix: PV prefix for the instrument.
        """
        self.host = host
        self.name = name
        self.pv_prefix = pv_prefix
        self.started = False
        self.stopped = False
        self.is_alive_flag = False

    def __repr__(self):
        return "name: {}, _host: {}, id: {}".format(self.name, self.host, id(self))

    def stop(self):
        self.stopped = True

    def start(self):
        self.started = True
        self.is_alive_flag = True

    def is_alive(self):
        return self.is_alive_flag

    def is_instrument(self, name, host):
        """
        Is this scrapper for this name and _host
        Args:
            name: name of the instrument
            host: _host of the instrument

        Returns: True is _host and name match; False otherwise

        """
        return self.name == name and self.host == host


class MockInstList(object):

    def __init__(self, instrument_host_dict):
        self.instrument_host_dict = instrument_host_dict

    def retrieve(self):
        return self.instrument_host_dict


class TestWebScrapperManager(unittest.TestCase):

    def setUp(self):
        self.expected_name = "inst"
        self.expected_host = "_host"
        self.expected_prefix = "_prefix"
        self.inst_list = MockInstList({self.expected_name: (self.expected_host, self.expected_prefix)})
        self.reader = Mock()

    def test_GIVEN_no_instruments_on_list_WHEN_run_THEN_no_web_scrapper_created(self):
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, MockInstList({}))

        web_scrapper_manager.maintain_scrapper_list()

        assert_that(web_scrapper_manager.scrappers, has_length(0))

    def test_GIVEN_one_instruments_on_list_WHEN_run_THEN_one_web_scrapper_created(self):

        web_scrapper_manager = WebScrapperManager(MockWebScrapper, self.inst_list)

        web_scrapper_manager.maintain_scrapper_list()

        assert_that(web_scrapper_manager.scrappers, has_length(1))
        assert_that(web_scrapper_manager.scrappers[0].name, is_(self.expected_name))
        assert_that(web_scrapper_manager.scrappers[0].host, is_(self.expected_host))
        assert_that(web_scrapper_manager.scrappers[0].pv_prefix, is_(self.expected_prefix))
        assert_that(web_scrapper_manager.scrappers[0].started, is_(True), "scrapper started")

    def test_GIVEN_three_instruments_on_list_WHEN_run_THEN_three_web_scrapper_created(self):
        expected_insts = {"inst1": ("_host", "_prefix"), "inst2": ("host2", "prefix2"), "inst3": ("host3", "prefix3")}
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, MockInstList(expected_insts))

        web_scrapper_manager.maintain_scrapper_list()

        result = {}
        for scrapper in web_scrapper_manager.scrappers:
            result[scrapper.name] = (scrapper.host, scrapper.pv_prefix)

        assert_that(result, is_(expected_insts))

    def test_GIVEN_one_instruments_on_list_which_already_has_a_scrapper_WHEN_run_THEN_no_web_scrapper_created(self):
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, self.inst_list)
        web_scrapper_manager.maintain_scrapper_list()
        original_scrapper = web_scrapper_manager.scrappers[0]

        web_scrapper_manager.maintain_scrapper_list()

        assert_that(web_scrapper_manager.scrappers, is_([original_scrapper]))

    def test_GIVEN_no_instruments_on_list_but_scrapper_exists_WHEN_run_THEN_web_scrapper_stopped_and_removed(self):
        inst_list = MockInstList({"inst": ("_host", "_prefix")})
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, inst_list)
        web_scrapper_manager.maintain_scrapper_list()

        inst_list.instrument_host_dict = {}
        original_scrapper = web_scrapper_manager.scrappers[0]

        web_scrapper_manager.maintain_scrapper_list()


        assert_that(web_scrapper_manager.scrappers, has_length(0))
        assert_that(original_scrapper.stopped, is_(True), "thread has been stopped")

    def test_GIVEN_one_instruments_on_list_which_has_same_host_name_as_a_scrapper_but_different_name_WHEN_run_THEN_only_one_new_scrapper_running(self):
        different_name = "diff"
        mock_inst_list = MockInstList({different_name: (self.expected_host, self.expected_prefix)})
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, mock_inst_list)
        web_scrapper_manager.maintain_scrapper_list()

        mock_inst_list.instrument_host_dict = {self.expected_name: (self.expected_host, self.expected_prefix)}

        web_scrapper_manager.maintain_scrapper_list()

        assert_that(web_scrapper_manager.scrappers, has_length(1))
        assert_that(web_scrapper_manager.scrappers[0].name, is_(self.expected_name))
        assert_that(web_scrapper_manager.scrappers[0].host, is_(self.expected_host))
        assert_that(web_scrapper_manager.scrappers[0].pv_prefix, is_(self.expected_prefix))

    def test_GIVEN_one_instruments_on_list_which_has_same_name_as_a_scrapper_but_different_host_WHEN_run_THEN_new_web_scrapper_created(self):
        different_host = "diff"
        different_prefix = "p_diff"
        mock_inst_list = MockInstList({self.expected_name: (different_host, different_prefix)})
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, mock_inst_list)
        web_scrapper_manager.maintain_scrapper_list()

        mock_inst_list.instrument_host_dict = {self.expected_name: (self.expected_host, self.expected_prefix)}

        web_scrapper_manager.maintain_scrapper_list()

        assert_that(web_scrapper_manager.scrappers, has_length(1))
        assert_that(web_scrapper_manager.scrappers[0].name, is_(self.expected_name))
        assert_that(web_scrapper_manager.scrappers[0].host, is_(self.expected_host))
        assert_that(web_scrapper_manager.scrappers[0].pv_prefix, is_(self.expected_prefix))

    def test_GIVEN_one_instruments_on_list_which_already_has_a_scrapper_but_scrapper_is_not_alive_WHEN_run_THEN_new_web_scrapper_created(self):
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, self.inst_list)
        web_scrapper_manager.maintain_scrapper_list()

        original_scrapper = web_scrapper_manager.scrappers[0]
        original_scrapper.is_alive_flag = False

        web_scrapper_manager.maintain_scrapper_list()


        assert_that(web_scrapper_manager.scrappers, not_(contains(original_scrapper)))
        assert_that(web_scrapper_manager.scrappers, has_length(1))
        assert_that(web_scrapper_manager.scrappers[0].name, is_(self.expected_name))
        assert_that(web_scrapper_manager.scrappers[0].host, is_(self.expected_host))
        assert_that(web_scrapper_manager.scrappers[0].pv_prefix, is_(self.expected_prefix))
        assert_that(web_scrapper_manager.scrappers[0].started, is_(True), "scrapper started")


if __name__ == '__main__':
    unittest.main()
