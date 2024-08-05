import binascii
import json
import os
import sys
import unittest
import zlib
from builtins import bytes

from CaChannel import CaChannelException
from hamcrest import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from external_webpage.web_scrapper_manager import InstList

caget_error = None
caget_value = ""

def caget(name, as_string):
    if caget_error is None:
        return caget_value
    raise caget_error


class TestInstList(unittest.TestCase):

    def setUp(self):
        global caget_value, caget_error

        self.inst_list = InstList(caget)
        caget_error = None
        caget_value = ""

    def compress_and_hex(self, value):
        """Compresses the inputted string and encodes it as hex.

        Args:
            value (string): The string to be compressed
        Returns:
            string : A compressed and hexed version of the inputted string
        """
        compr = zlib.compress(bytes(value, 'utf-8'))
        return binascii.hexlify(bytearray(compr))

    def test_GIVEN_caget_contains_one_instrument_WHEN_retrive_THEN_list_returned(self):
        global caget_value, caget_error

        instrument = "INST"
        host_name = "NDXINST"
        prefix = "IN:INST:"
        caget_value = self.compress_and_hex(json.dumps([{"pvPrefix": prefix, "hostName": host_name, "name": instrument}]))

        list = self.inst_list.retrieve()

        assert_that(list, is_({instrument: (host_name, prefix)}))

    def test_GIVEN_caget_throws_not_connected_and_no_cached_values_WHEN_retrive_THEN_empty_cached_list_returned(self):
        global caget_value, caget_error

        caget_error = CaChannelException(1)

        list = self.inst_list.retrieve()

        assert_that(list, is_({}))
        assert_that(self.inst_list.error_on_retrieve, is_(InstList.INSTRUMENT_LIST_CAN_NOT_BE_READ))

    def test_GIVEN_caget_contains_non_hex_string_WHEN_retrive_THEN_empty_cached_list_returned(self):
        global caget_value, caget_error

        caget_value = "hjkdfhui"

        list = self.inst_list.retrieve()

        assert_that(list, is_({}))
        assert_that(self.inst_list.error_on_retrieve, is_(InstList.INSTRUMENT_LIST_NOT_DECOMPRESSED))

    def test_GIVEN_caget_contains_non_compresed_string_WHEN_retrive_THEN_empty_cached_list_returned(self):
        global caget_value, caget_error

        caget_value = "23678164"

        list = self.inst_list.retrieve()

        assert_that(list, is_({}))
        assert_that(self.inst_list.error_on_retrieve, is_(InstList.INSTRUMENT_LIST_NOT_DECOMPRESSED))

    def test_GIVEN_caget_contains_non_json_inst_list_WHEN_retrive_THEN_empty_cached_list_returned(self):
        global caget_value, caget_error

        caget_value = self.compress_and_hex("not json")

        list = self.inst_list.retrieve()

        assert_that(list, is_({}))
        assert_that(self.inst_list.error_on_retrieve, is_(InstList.INSTRUMENT_LIST_NOT_JSON))


    def test_GIVEN_caget_contains_nonsense_inst_list_WHEN_retrive_THEN_empty_cached_list_returned(self):
        global caget_value, caget_error

        caget_value = self.compress_and_hex(json.dumps([{"pvPrefix": "IN:INST:", "hostName": "host"}]))

        list = self.inst_list.retrieve()

        assert_that(list, is_({}))
        assert_that(self.inst_list.error_on_retrieve, is_(InstList.INSTRUMENT_LIST_NOT_CORRECT_FORMAT))

    def test_GIVEN_caget_contains_instrument_then_has_error_WHEN_retrive_THEN_first_cached_list_returned(self):
        global caget_value, caget_error

        instrument = "INST"
        host_name = "NDXINST"
        prefix = "IN:INST:"
        caget_value = self.compress_and_hex(json.dumps([{"pvPrefix": prefix, "hostName": host_name, "name": instrument}]))
        self.inst_list.retrieve()

        caget_error = CaChannelException(1)
        list = self.inst_list.retrieve()

        assert_that(list, is_({instrument: (host_name, prefix)}))
        assert_that(self.inst_list.error_on_retrieve, is_(InstList.INSTRUMENT_LIST_CAN_NOT_BE_READ))


if __name__ == '__main__':
    unittest.main()
