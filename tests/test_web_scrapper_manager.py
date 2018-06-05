import os
import sys
from hamcrest import *
import unittest

from mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from external_webpage.web_scrapper_manager import WebScrapperManager


class MockWebScrapper(object):
    pass


class MockInstListGetter(object):
    pass


class TestWebScrapperManager(unittest.TestCase):

    def setUp(self):
        self.reader = Mock()

    def test_GIVEN_no_instruments_on_list_WHEN_run_THEN_no_web_scrapper_created(self):

        web_scrapper_manager = WebScrapperManager(MockWebScrapper, MockInstListGetter)

        web_scrapper_manager.run()

        assert_that(web_scrapper_manager.scrappers, has_length(0))


if __name__ == '__main__':
    unittest.main()
