import os
import sys
import unittest

from hamcrest import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from external_webpage.web_page_parser import WebPageParser, BlocksParseError
from tests.data_mother import ArchiveMother


class TestBlocksFromJSON(unittest.TestCase):


    def test_GIVEN_no_object_WHEN_parse_THEN_exception(self):
        json = {}
        parser = WebPageParser()

        try:
            parser.extract_blocks(json)
            self.fail("Should have thrown exception")
        except BlocksParseError:
            pass

    def test_GIVEN_no_channels_WHEN_parse_THEN_channels_are_blank(self):
        json = ArchiveMother.create_info_page([])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        self.assertEqual(len(result), 0, "Length of result" )

    def test_GIVEN_one_channels_WHEN_parse_THEN_blocks_contain_channel(self):
        expected_name = "BLOCK"
        json = ArchiveMother.create_info_page([ArchiveMother.create_channel(expected_name)])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result, has_length(1))
        assert_that(result[expected_name].name, is_(expected_name))

    def test_GIVEN_one_channels_is_diconnected_WHEN_parse_THEN_block_is_disconnected(self):
        expected_name = "BLOCK"
        expected_connectivity = False
        json = ArchiveMother.create_info_page(
            [ArchiveMother.create_channel(name=expected_name, is_connected=expected_connectivity)])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result[expected_name].is_connected(), is_(expected_connectivity))

    def test_GIVEN_one_channels_is_connected_WHEN_parse_THEN_block_is_connected(self):
        expected_name = "BLOCK"
        expected_connectivity = True
        json = ArchiveMother.create_info_page(
            [ArchiveMother.create_channel(name=expected_name, is_connected=expected_connectivity)])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result[expected_name].is_connected(), is_(expected_connectivity))

    def test_GIVEN_one_channels_has_value_WHEN_parse_THEN_block_has_value(self):
        expected_name = "BLOCK"
        expected_value = u"5.4"
        json = ArchiveMother.create_info_page([ArchiveMother.create_channel(name=expected_name, value=expected_value)])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result[expected_name].get_value(), is_(expected_value))

    def test_GIVEN_one_channels_is_disconnected_WHEN_parse_THEN_block_has_value_null(self):
        expected_name = "BLOCK"
        expected_connectivity = False
        expected_value = u"null"
        json = ArchiveMother.create_info_page([
            ArchiveMother.create_channel(name=expected_name, value=expected_value, is_connected=expected_connectivity)])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result[expected_name].get_value(), is_(expected_value))

    def test_GIVEN_one_channels_in_alarm_WHEN_parse_THEN_block_has_alarm(self):
        expected_name = "BLOCK"
        expected_alarm = u"INVALID/UDF_ALARM"
        json = ArchiveMother.create_info_page([ArchiveMother.create_channel(name=expected_name, alarm=expected_alarm)])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result[expected_name].get_alarm(), is_(expected_alarm))

    def test_GIVEN_one_channels_with_units_WHEN_parse_THEN_block_has_units(self):
        expected_name = "BLOCK"
        units = u'uA hour'
        value = u'0.000'
        expected_value = "{} {}".format(value, units)
        json = ArchiveMother.create_info_page([ArchiveMother.create_channel(name=expected_name, units=units, value=value)])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result[expected_name].get_description()["value"], is_(expected_value))

    def test_GIVEN_one_channels_WHEN_parse_THEN_block_is_visible(self):
        expected_name = "BLOCK"
        json = ArchiveMother.create_info_page([ArchiveMother.create_channel(expected_name)])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result[expected_name].get_visibility(), is_(True))

    def test_GIVEN_multiple_channels_WHEN_parse_THEN_have_mulitple_blocks_containing_all_info(self):
        expected_names = ["BLOCK1", "block_2", "block3"]
        expected_expected_connectivities = [True, True, False]
        given_values = ["0.001", "hello", "null"]
        given_units = ["mA", "", ""]
        expected_values = ["0.001 mA", "hello", "null"]
        expected_alarm = ["", "MINOR/LOW", ""]
        channels = []
        for name, connectivity, value, units, alarm in zip(expected_names, expected_expected_connectivities, given_values, given_units, expected_alarm):
            channels.append(
                ArchiveMother.create_channel(name=name, is_connected=connectivity, units=units, alarm=alarm, value=value))

        json = ArchiveMother.create_info_page(channels)
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result, has_length(len(expected_names)))
        for name, connectivity, expected_value, alarm in zip(expected_names, expected_expected_connectivities, expected_values, expected_alarm):
            assert_that(result[name].get_name(), is_(name))
            assert_that(result[name].get_alarm(), is_(alarm))
            assert_that(result[name].is_connected(), is_(connectivity))
            assert_that(result[name].get_description()["value"], is_(expected_value))
            assert_that(result[name].get_visibility(), is_(True))


    def test_GIVEN_one_invalid_channels_WHEN_parse_THEN_no_blocks_returned(self):
        expected_name = "BLOCK"
        json = ArchiveMother.create_info_page([None])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result, has_length(0))

    def test_GIVEN_one_channels_with_no_units_but_connected_WHEN_parse_THEN_block_has_units(self):
        """
        e.g. CS:PS: PVs
        """
        expected_name = "BLOCK"
        value = u'0.000'
        expected_value = "{}".format(value)
        channel = ArchiveMother.create_channel(name=expected_name, value=value)
        del channel['Current Value']["Units"]
        json = ArchiveMother.create_info_page([channel])
        parser = WebPageParser()

        result = parser.extract_blocks(json)

        assert_that(result[expected_name].get_description()["value"], is_(expected_value))



#{"Enabled":true,"Channels":[{"Channel":"TE:NDW1798:CS:SB:NEW_BLOCK","Connected":true,"Internal State":"Connected","Mechanism":"30.00 sec scan, max. 60 repeats","Current Value":{"Timestamp":"2017-10-19 09:04:16.141466495","Value":"0.000","Units":"uA hour","Alarm":""},"Last Archived Value":{"Timestamp":"2017-10-19 15:50:58.305000000","Value":"0.000","Units":"uA hour","Alarm":""},"Received Values":1,"State":true,"Queue Len.":0,"Queue Avg.":0.020589113209464906,"Queue Max.":1,"Capacity":2,"Overruns":0},{"Channel":"TE:NDW1798:CS:SB:NEW_BLOCK_1","Connected":true,"Internal State":"Connected","Mechanism":"30.00 sec scan, max. 60 repeats","Current Value":{"Timestamp":"2017-10-19 09:04:16.141466495","Value":"0.000","Units":"uA hour","Alarm":""},"Last Archived Value":{"Timestamp":"2017-10-19 15:50:58.305000000","Value":"0.000","Units":"uA hour","Alarm":""},"Received Values":1,"State":true,"Queue Len.":0,"Queue Avg.":0.020589113209464906,"Queue Max.":1,"Capacity":2,"Overruns":0},{"Channel":"TE:NDW1798:CS:SB:NEW_BLOCK_2","Connected":true,"Internal State":"Connected","Mechanism":"30.00 sec scan, max. 60 repeats","Current Value":{"Timestamp":"2017-10-19 09:04:16.141466495","Value":"0.000","Units":"uA hour","Alarm":""},"Last Archived Value":{"Timestamp":"2017-10-19 15:50:58.305000000","Value":"0.000","Units":"uA hour","Alarm":""},"Received Values":1,"State":true,"Queue Len.":0,"Queue Avg.":0.020589113209464906,"Queue Max.":1,"Capacity":2,"Overruns":0},{"Channel":"TE:NDW1798:CS:SB:NEW_BLOCK_3","Connected":true,"Internal State":"Connected","Mechanism":"30.00 sec scan, max. 60 repeats","Current Value":{"Timestamp":"2017-10-19 11:50:58.068000000","Value":"0","Units":"","Alarm":"INVALID/UDF_ALARM"},"Last Archived Value":{"Timestamp":"2017-10-19 15:50:58.305000000","Value":"0","Units":"","Alarm":"INVALID/UDF_ALARM"},"Received Values":1,"State":true,"Queue Len.":0,"Queue Avg.":0.020589113209464906,"Queue Max.":1,"Capacity":2,"Overruns":0},{"Channel":"TE:NDW1798:CS:SB:NEW_BLOCK_4","Connected":true,"Internal State":"Connected","Mechanism":"30.00 sec scan, max. 60 repeats","Current Value":{"Timestamp":"2017-10-19 11:50:58.079000000","Value":"0","Units":"","Alarm":"INVALID/UDF_ALARM"},"Last Archived Value":{"Timestamp":"2017-10-19 15:50:58.305000000","Value":"0","Units":"","Alarm":"INVALID/UDF_ALARM"},"Received Values":1,"State":true,"Queue Len.":0,"Queue Avg.":0.020589113209464906,"Queue Max.":1,"Capacity":2,"Overruns":0}]}
if __name__ == '__main__':
    unittest.main()
