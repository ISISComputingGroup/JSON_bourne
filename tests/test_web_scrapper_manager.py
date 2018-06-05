import os
import sys
from hamcrest import *
import unittest

from mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from external_webpage.web_scrapper_manager import WebScrapperManager


class MockWebScrapper(object):
    def __init__(self, name, host):
        """
        Initialize.
        Args:
            name: Name of instrument.
            host: Host for the instrument.
        """
        self.host = host
        self.name = name
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
        self.reader = Mock()

    def test_GIVEN_no_instruments_on_list_WHEN_run_THEN_no_web_scrapper_created(self):
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, MockInstList({}))

        web_scrapper_manager.run()

        assert_that(web_scrapper_manager.scrappers, has_length(0))

    def test_GIVEN_one_instruments_on_list_WHEN_run_THEN_one_web_scrapper_created(self):
        expected_name = "inst"
        expected_host = "_host"
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, MockInstList({expected_name: expected_host}))

        web_scrapper_manager.run()

        assert_that(web_scrapper_manager.scrappers, has_length(1))
        assert_that(web_scrapper_manager.scrappers[0].name, is_(expected_name))
        assert_that(web_scrapper_manager.scrappers[0].host, is_(expected_host))
        assert_that(web_scrapper_manager.scrappers[0].started, is_(True), "scrapper started")

    def test_GIVEN_three_instruments_on_list_WHEN_run_THEN_three_web_scrapper_created(self):
        expected_insts = {"inst1": "_host", "inst2": "host2", "inst3": "host3"}
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, MockInstList(expected_insts))

        web_scrapper_manager.run()

        result = {}
        for scrapper in web_scrapper_manager.scrappers:
            result[scrapper.name] = scrapper.host

        assert_that(result, is_(expected_insts))

    def test_GIVEN_one_instruments_on_list_which_already_has_a_scrapper_WHEN_run_THEN_no_web_scrapper_created(self):
        expected_name = "inst"
        expected_host = "_host"
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, MockInstList({expected_name: expected_host}))
        web_scrapper_manager.run()
        original_scrapper = web_scrapper_manager.scrappers[0]

        web_scrapper_manager.run()

        assert_that(web_scrapper_manager.scrappers, is_([original_scrapper]))

    def test_GIVEN_no_instruments_on_list_but_scrapper_exists_WHEN_run_THEN_web_scrapper_stopped_and_removed(self):
        inst_list = MockInstList({"inst": "_host"})
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, inst_list)
        web_scrapper_manager.run()
        inst_list.instrument_host_dict = {}
        original_scrapper = web_scrapper_manager.scrappers[0]

        web_scrapper_manager.run()

        assert_that(web_scrapper_manager.scrappers, has_length(0))
        assert_that(original_scrapper.stopped, is_(True), "thread has been stopped")

    def test_GIVEN_one_instruments_on_list_which_has_same_host_name_as_a_scrapper_but_different_name_WHEN_run_THEN_only_one_new_scrapper_running(self):
        expected_name = "inst"
        expected_host = "_host"
        different_name = "diff"
        mock_inst_list = MockInstList({different_name: expected_host})
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, mock_inst_list)
        web_scrapper_manager.run()
        mock_inst_list.instrument_host_dict = {expected_name: expected_host}

        web_scrapper_manager.run()

        assert_that(web_scrapper_manager.scrappers, has_length(1))
        assert_that(web_scrapper_manager.scrappers[0].name, is_(expected_name))
        assert_that(web_scrapper_manager.scrappers[0].host, is_(expected_host))

    def test_GIVEN_one_instruments_on_list_which_has_same_name_as_a_scrapper_but_different_host_WHEN_run_THEN_new_web_scrapper_created(self):
        expected_name = "inst"
        expected_host = "_host"
        different_host = "diff"
        mock_inst_list = MockInstList({expected_name: different_host})
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, mock_inst_list)
        web_scrapper_manager.run()
        mock_inst_list.instrument_host_dict = {expected_name: expected_host}

        web_scrapper_manager.run()

        assert_that(web_scrapper_manager.scrappers, has_length(1))
        assert_that(web_scrapper_manager.scrappers[0].name, is_(expected_name))
        assert_that(web_scrapper_manager.scrappers[0].host, is_(expected_host))

    def test_GIVEN_one_instruments_on_list_which_already_has_a_scrapper_but_scrapper_is_not_alive_WHEN_run_THEN_new_web_scrapper_created(self):
        expected_name = "inst"
        expected_host = "_host"
        web_scrapper_manager = WebScrapperManager(MockWebScrapper, MockInstList({expected_name: expected_host}))
        web_scrapper_manager.run()
        original_scrapper = web_scrapper_manager.scrappers[0]
        original_scrapper.is_alive_flag = False

        web_scrapper_manager.run()

        assert_that(web_scrapper_manager.scrappers, not_(contains(original_scrapper)))
        assert_that(web_scrapper_manager.scrappers, has_length(1))
        assert_that(web_scrapper_manager.scrappers[0].name, is_(expected_name))
        assert_that(web_scrapper_manager.scrappers[0].host, is_(expected_host))
        assert_that(web_scrapper_manager.scrappers[0].started, is_(True), "scrapper started")


if __name__ == '__main__':
    unittest.main()
