import os
import sys
from hamcrest import *
import unittest

from mock import Mock

from external_webpage.get_webpage import WebPageScraper

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from external_webpage.web_page_parser import WebPageParser, BlocksParseError
from tests.data_mother import ArchiveMother, ConfigMother

class TestBlocksFromJSON(unittest.TestCase):


    def setUp(self):
        self.reader = Mock()
        page_info = ArchiveMother.create_info_page([])
        self.reader.get_info = Mock(return_value=page_info)

        config = ConfigMother.create_config()
        self.reader.read_config = Mock(return_value=config)

        self.scraper = WebPageScraper(reader=self.reader)

    def test_GIVEN_no_blocks_WHEN_parse_THEN_normal_value_returned(self):
        expected_config_name = "test_config"
        config = ConfigMother.create_config(name=expected_config_name)
        self.reader.read_config = Mock(return_value=config)

        result = self.scraper.scrape_webpage()

        assert_that(result["config_name"], expected_config_name)

    def test_GIVEN_run_duraction_WHEN_parse_THEN_correctly_formatted_duration_returned(self):
        name = "DAE:RUNDURATION.VAL"
        value = 5025
        units = "s"
        expected_value = "1 hr 23 min 45 s"
        def get_test_info(port, groupname):
            if groupname == "INST":
                return ArchiveMother.create_info_page([ArchiveMother.create_channel(name=name, value=value, units=units)])
            else:
                return ArchiveMother.create_info_page([])

        self.reader.get_info = Mock(side_effect=get_test_info)

        result = self.scraper.scrape_webpage()

        assert_that(result["inst_pvs"]["RUNDURATION"]["value"], is_(expected_value))


if __name__ == '__main__':
    unittest.main()
