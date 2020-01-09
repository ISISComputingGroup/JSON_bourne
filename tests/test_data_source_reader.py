import unittest
from mock import MagicMock, patch
from external_webpage.data_source_reader import DataSourceReader
from hamcrest import *


def patch_page_contents(request_response, json):
    page = MagicMock()
    page.content = json
    request_response.return_value = page


class TestDataSourceReader(unittest.TestCase):
    def setUp(self):
        self.reader = DataSourceReader("HOST")

    @patch("requests.get")
    def test_GIVEN_JSON_with_single_quotes_WHEN_read_THEN_conversion_successful(self, request_response):
        patch_page_contents(request_response, b"{'data': 'some_data'}")

        json_object = self.reader.read_config()

        assert_that(json_object, is_({"data": "some_data"}))

    @patch("requests.get")
    def test_GIVEN_JSON_with_None_WHEN_read_THEN_conversion_successful(self, request_response):
        patch_page_contents(request_response, b'{"data": None}')

        json_object = self.reader.read_config()

        assert_that(json_object, is_({"data": None}))

    @patch("requests.get")
    def test_GIVEN_JSON_with_True_WHEN_read_THEN_conversion_successful(self, request_response):
        patch_page_contents(request_response, b'{"data": True}')

        json_object = self.reader.read_config()

        assert_that(json_object, is_({"data": True}))

    @patch("requests.get")
    def test_GIVEN_JSON_with_False_WHEN_read_THEN_conversion_successful(self, request_response):
        patch_page_contents(request_response, b'{"data": False}')

        json_object = self.reader.read_config()

        assert_that(json_object, is_({"data": False}))
