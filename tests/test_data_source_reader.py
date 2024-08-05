import binascii
import unittest
import zlib

from hamcrest import *
from mock import MagicMock, patch

from external_webpage.data_source_reader import DataSourceReader


def patch_page_contents(request_response, json):
    page = MagicMock()
    page.content = json
    request_response.return_value = page


def compress_and_hex(value):
    """Compresses the inputted string and encodes it as hex.

    Args:
        value (str): The string to be compressed
    Returns:
        bytes : A compressed and hexed version of the inputted string
    """
    assert type(value) == str, \
        "Non-str argument passed to compress_and_hex, maybe Python 2/3 compatibility issue\n" \
        "Argument was type {} with value {}".format(value.__class__.__name__, value)
    compr = zlib.compress(bytes(value, "utf-8"))
    return binascii.hexlify(compr)


class TestDataSourceReader(unittest.TestCase):
    def setUp(self):
        self.reader = DataSourceReader("HOST", "PREFIX")

    @patch("requests.get")
    @patch("external_webpage.data_source_reader.caget")
    def test_GIVEN_JSON_with_single_quotes_WHEN_read_THEN_conversion_successful(self, caget, request_response):
        patch_page_contents(request_response, b"{'data': 'some_data'}")

        json_object = self.reader.read_config()

        assert_that(json_object, is_({"data": "some_data"}))

    @patch("requests.get")
    @patch("external_webpage.data_source_reader.caget")
    def test_GIVEN_JSON_with_None_WHEN_read_THEN_conversion_successful(self, caget, request_response):
        patch_page_contents(request_response, b'{"data": None}')

        json_object = self.reader.read_config()

        assert_that(json_object, is_({"data": None}))

    @patch("requests.get")
    @patch("external_webpage.data_source_reader.caget")
    def test_GIVEN_JSON_with_True_WHEN_read_THEN_conversion_successful(self, caget, request_response):
        patch_page_contents(request_response, b'{"data": True}')

        json_object = self.reader.read_config()

        assert_that(json_object, is_({"data": True}))

    @patch("requests.get")
    @patch("external_webpage.data_source_reader.caget")
    def test_GIVEN_JSON_with_False_WHEN_read_THEN_conversion_successful(self, caget, request_response):
        patch_page_contents(request_response, b'{"data": False}')

        json_object = self.reader.read_config()

        assert_that(json_object, is_({"data": False}))

    @patch("requests.get")
    @patch("external_webpage.data_source_reader.caget")
    def test_GIVEN_valid_config_from_caget_WHEN_read_THEN_webserver_is_not_tried(self, caget, request_response):
        caget.return_value = compress_and_hex('{"data": false}')

        json_object = self.reader.read_config()

        assert_that(json_object, is_({"data": False}))
        request_response.assert_not_called()
