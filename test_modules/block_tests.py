# This file is part of the ISIS IBEX application.
# Copyright (C) 2012-2016 Science & Technology Facilities Council.
# All rights reserved.
#
# This program is distributed in the hope that it will be useful.
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution.
# EXCEPT AS EXPRESSLY SET FORTH IN THE ECLIPSE PUBLIC LICENSE V1.0, THE PROGRAM
# AND ACCOMPANYING MATERIALS ARE PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND.  See the Eclipse Public License v1.0 for more details.
#
# You should have received a copy of the Eclipse Public License v1.0
# along with this program; if not, you can obtain a copy from
# https://www.eclipse.org/org/documents/epl-v10.php or
# http://opensource.org/licenses/eclipse-1.0.php

import unittest
from datetime import datetime
from block import Block


class TestGetWebpage(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_GIVEN_empty_status_WHEN_block_from_raw_THEN_returned_block_has_empty_status(self):
        empty_string = ""
        self.assertEqual(empty_string, Block.from_raw("title", empty_string, "raw").get_status())

    def test_GIVEN_none_status_WHEN_block_from_raw_THEN_returned_block_has_none_status(self):
        none_object = None
        self.assertEqual(none_object, Block.from_raw("title", none_object, "raw").get_status())

    def test_GIVEN_null_status_WHEN_block_from_raw_THEN_returned_block_has_null_status(self):
        null_string = "null"
        self.assertEqual(null_string, Block.from_raw("title", null_string, "raw").get_status())

    def test_GIVEN_empty_value_WHEN_block_from_raw_THEN_block_returned(self):
        self.assertIsNotNone(Block.from_raw("", "status", "raw"))

    def test_GIVEN_none_title_WHEN_block_from_raw_THEN_block_returned(self):
        self.assertIsNotNone(Block.from_raw(None, "status", "raw"))

    def test_GIVEN_null_title_WHEN_block_from_raw_THEN_block_returned(self):
        self.assertIsNotNone(Block.from_raw("null", "status", "raw"))

    def _test_GIVEN_object_WHEN_block_from_raw_THEN_default_constructor_values_used(self, raw_object):
        # Arrange
        null_string = "null"
        null_date = datetime(1970,1,1)

        # Act
        test_block = Block.from_raw("title", "status", raw_object)

        # Assert
        self.assertEqual(null_string,test_block.get_alarm())
        self.assertEqual(null_string,test_block.get_value())
        self.assertEqual(null_date,test_block.get_change_datetime())

    def test_GIVEN_empty_raw_block_WHEN_block_from_raw_THEN_returned_block_null_string_value_and_alarm_and_1_1_1970_date(self):
        self._test_GIVEN_object_WHEN_block_from_raw_THEN_default_constructor_values_used("")

    def test_GIVEN_none_raw_block_WHEN_block_from_raw_THEN_returned_block_null_string_value_and_alarm_and_1_1_1970_date(self):
        self._test_GIVEN_object_WHEN_block_from_raw_THEN_default_constructor_values_used("null")

    def test_GIVEN_null_raw_block_WHEN_block_from_raw_THEN_returned_block_null_string_value_and_alarm_and_1_1_1970_date(self):
        self._test_GIVEN_object_WHEN_block_from_raw_THEN_default_constructor_values_used(None)

    @staticmethod
    def _get_dict_of_standard_values():
        return {"date": "2016/11/18", "time": "12:26:30.732319800",
                "value": "40.000", "connected": "OK", "alarm": "OK"}

    @staticmethod
    def _get_standard_value_string():
        dict_of_values = TestGetWebpage._get_dict_of_standard_values()
        return " ".join([dict_of_values[key]
                         for key in ["date","time","value", "connected", "alarm"]])

    @staticmethod
    def _get_block_from_raw_standard_value_string():
        return Block.from_raw("title", "status", TestGetWebpage._get_standard_value_string())

    def test_GIVEN_standard_format_input_WHEN_block_from_raw_THEN_returned_block_has_expected_alarm(self):
        self.assertEqual(TestGetWebpage._get_dict_of_standard_values()["alarm"],
                         TestGetWebpage._get_block_from_raw_standard_value_string().get_alarm())

    def test_GIVEN_standard_format_input_WHEN_block_from_raw_THEN_returned_block_has_expected_value(self):
        self.assertEqual(TestGetWebpage._get_dict_of_standard_values()["value"],
                         TestGetWebpage._get_block_from_raw_standard_value_string().get_value())

    def test_GIVEN_standard_format_input_WHEN_block_from_raw_THEN_returned_block_has_expected_date(self):
        self.assertEqual(TestGetWebpage._get_dict_of_standard_values()["date"],
                         TestGetWebpage._get_block_from_raw_standard_value_string().
                         get_change_datetime().strftime("%Y/%m/%d"))

    def test_GIVEN_standard_format_input_WHEN_block_from_raw_THEN_returned_block_has_time_stripped_of_nanoseconds(self):
        self.assertEqual(TestGetWebpage._get_dict_of_standard_values()["time"][:-3],
                         str(TestGetWebpage._get_block_from_raw_standard_value_string().get_change_datetime().time()))





if __name__ == '__main__':
    # Run tests
    unittest.main()