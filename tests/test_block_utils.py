#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from builtins import str

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest

from mock import MagicMock

from block import Block
from block_utils import format_block_value, format_blocks, set_rc_values_for_blocks, shorten_title


class TestBlockUtils(unittest.TestCase):
    def test_format_blocks_with_two_blocks(self):
        # Arrange
        test_blocks = {
            "NEW_BLOCK": Block("NEW_BLOCK", "INVALID", "10", "UDF_ALARM", False, None),
            "NOT_NEW_BLOCK": Block("NOT_NEW_BLOCK", "GOOD", "100", "NO_ALARM", False, None),
        }
        expected_result = {
            "NEW_BLOCK": {
                "status": "INVALID",
                "alarm": "UDF_ALARM",
                "visibility": False,
                "value": "10",
                "rc_enabled": "NO",
            },
            "NOT_NEW_BLOCK": {
                "status": "GOOD",
                "alarm": "NO_ALARM",
                "visibility": False,
                "value": "100",
                "rc_enabled": "NO",
            },
        }

        # Act
        formatted_blocks = format_blocks(test_blocks)

        # Assert
        self._assert_blocks(formatted_blocks, expected_result)

    def test_format_blocks_with_one_block(self):
        # Arrange
        test_blocks = {"NEW_BLOCK": Block("NEW_BLOCK", "", "10", "", False, None)}
        expected_result = {
            "NEW_BLOCK": {
                "status": "",
                "alarm": "",
                "visibility": False,
                "value": "10",
                "rc_enabled": "NO",
            },
        }

        # Act
        formatted_blocks = format_blocks(test_blocks)

        # Assert
        self._assert_blocks(formatted_blocks, expected_result)

    def test_format_blocks_with_one_block_with_rc_values(self):
        # Arrange
        block = Block("NEW_BLOCK", "", 10, "", False, None)
        block.set_rc_low(0)
        block.set_rc_high(100)
        block.set_rc_inrange(False)
        block.set_rc_enabled("YES")

        test_blocks = {"NEW_BLOCK": block}
        expected_result = {
            "NEW_BLOCK": {
                "status": "",
                "alarm": "",
                "visibility": False,
                "value": "10",
                "rc_high": 100,
                "rc_low": 0,
                "rc_inrange": False,
                "rc_enabled": "YES",
            },
        }

        # Act
        formatted_blocks = format_blocks(test_blocks)

        # Assert
        self._assert_blocks(formatted_blocks, expected_result)

    def test_format_blocks_with_two_blocks_with_rc_values(self):
        # Arrange
        block1 = Block("NEW_BLOCK", "", 10, "", False)
        block1.set_rc_low(10)
        block1.set_rc_high(20)
        block1.set_rc_inrange(True)
        block1.set_rc_enabled("YES")

        block2 = Block("OLD_BLOCK", "", 10, "", False)
        block2.set_rc_low(0)
        block2.set_rc_high(100)
        block2.set_rc_inrange(False)

        test_blocks = {"NEW_BLOCK": block1, "OLD_BLOCK": block2}

        expected_result = {
            "NEW_BLOCK": {
                "status": "",
                "alarm": "",
                "visibility": False,
                "value": "10",
                "rc_high": 20,
                "rc_low": 10,
                "rc_inrange": True,
                "rc_enabled": "YES",
            },
            "OLD_BLOCK": {
                "status": "",
                "alarm": "",
                "visibility": False,
                "value": "10",
                "rc_high": 100,
                "rc_low": 0,
                "rc_inrange": False,
                "rc_enabled": "NO",
            },
        }

        # Act
        formatted_blocks = format_blocks(test_blocks)

        # Assert
        self._assert_blocks(formatted_blocks, expected_result)

    def test_format_blocks_with_empty_dict(self):
        # Arrange
        test_blocks = {}
        expected_result = {}

        # Act
        formatted_blocks = format_blocks(test_blocks)

        # Assert
        self.assertEqual(formatted_blocks, expected_result)

    def test_GIVEN_dict_of_ordered_blocks_WHEN_formatted_blocks_called_THEN_return_same_block_order(
        self,
    ):
        # Arrange
        test_blocks = {"Block 1": MagicMock(), "Block 2": MagicMock(), "Block 3": MagicMock()}

        expected_order_blocks = {
            "Block 1": MagicMock(),
            "Block 2": MagicMock(),
            "Block 3": MagicMock(),
        }

        # Act
        formatted_blocks = format_blocks(test_blocks)

        # Assert
        self.assertSequenceEqual(expected_order_blocks.keys(), formatted_blocks.keys())

    def test_shorten_title_for_default_case(self):
        # Arrange
        test_pv = "TE:NDLT910:DAE:COUNTRATE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "COUNTRATE.VAL")

    def test_shorten_title_with_rc_in_range(self):
        # Arrange
        test_pv = "TE:NDLT910:CS:SB:NEW_BLOCK:RC:INRANGE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "NEW_BLOCK:RC:INRANGE.VAL")

    def test_shorten_title_with_rc_enabled(self):
        # Arrange
        test_pv = "TE:NDLT910:CS:SB:NEW_BLOCK:RC:ENABLE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "NEW_BLOCK:RC:ENABLE.VAL")

    def test_shorten_title_with_rc_in_range(self):
        # Arrange
        test_pv = "TE:NDLT910:CS:SB:OLD_BLOCK:RC:INRANGE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "OLD_BLOCK:RC:INRANGE.VAL")

    def test_shorten_title_with_empty_string(self):
        # Arrange
        test_pv = ""

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "")

    def test_shorten_title_with_bad_rc_value(self):
        # Arrange
        test_pv = "OLD_BLOCK:RC:OUTRANGE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "OUTRANGE.VAL")

    def test_shorten_title_with_malformed_input_end_of_title(self):
        # Arrange
        test_pv = "INRANGE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "INRANGE.VAL")

    def test_shorten_title_with_malformed_input_rc_value(self):
        # Arrange
        test_pv = "RC:INRANGE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "RC:INRANGE.VAL")

    def test_shorten_title_rc_in_pv_doesnt_count(self):
        # Arrange
        test_pv = "TE:NDLT910:RC.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "RC.VAL")

    def test_shorten_title_larmor_block_high_rc(self):
        # Arrange
        test_pv = "IN:LARMOR:CS:SB:CJHCent:RC:HIGH.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "CJHCent:RC:HIGH.VAL")

    def test_shorten_title_larmor_block_low_rc(self):
        # Arrange
        test_pv = "IN:LARMOR:CS:SB:Chi:RC:LOW.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEqual(shortened_title, "Chi:RC:LOW.VAL")

    def test_when_rc_values_given_block_description_contains_rc_values(self):
        # Arrange
        test_block = Block("TEST", "INVALID", "10", "UDF_ALARM", "OFF")
        test_block.set_rc_low(0)
        test_block.set_rc_high(100)
        test_block.set_rc_inrange(False)

        # Act
        description = test_block.get_description()

        # Assert
        self.assertEqual(description["visibility"], "OFF")
        self.assertEqual(description["status"], "INVALID")
        self.assertEqual(description["alarm"], "UDF_ALARM")
        self.assertEqual(description["rc_low"], 0)
        self.assertEqual(description["rc_high"], 100)
        self.assertEqual(description["rc_inrange"], False)

    def test_when_rc_values_not_given_block_description_do_not_contain_rc_values(self):
        # Arrange
        test_block = Block("TEST", "INVALID", "10", "UDF_ALARM", "OFF")

        # Act
        description = test_block.get_description()

        # Assert
        self.assertEqual(description["visibility"], "OFF")
        self.assertEqual(description["status"], "INVALID")
        self.assertEqual(description["alarm"], "UDF_ALARM")
        self.assertTrue("rc_low" not in description)
        self.assertTrue("rc_high" not in description)
        self.assertTrue("rc_inrange" not in description)

    def test_set_rc_low_value_for_block_based_on_pv(self):
        # Arrange
        block_name = "NEW_BLOCK"
        expected_value = 10
        blocks = {block_name: Block(block_name, "", "", "", "")}
        runcontrol = {
            "{}:RC:LOW.VAL".format(block_name): Block("", "", expected_value, "", ""),
            "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
            "NEW_BLOCK:SOMETHINGELSE.VAL": Block("", "", False, "", ""),
            "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", ""),
        }

        # Act
        set_rc_values_for_blocks(blocks, runcontrol)

        # Assert
        self.assertEqual(blocks[block_name].get_rc_low(), expected_value)

    def test_set_rc_high_value_for_block_based_on_pv(self):
        # Arrange
        block_name = "NEW_BLOCK"
        blocks = {block_name: Block(block_name, "", "", "", "")}
        runcontrol = {
            "{}:RC:LOW.VAL".format(block_name): Block("", "", 10, "", ""),
            "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
            "{}:SOMETHINGELSE.VAL".format(block_name): Block("", "", False, "", ""),
            "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", ""),
            "{}:RC:HIGH.VAL".format(block_name): Block("", "", 100, "", ""),
        }

        # Act
        set_rc_values_for_blocks(blocks, runcontrol)

        # Assert
        self.assertEqual(blocks[block_name].get_rc_low(), 10)
        self.assertEqual(blocks[block_name].get_rc_high(), 100)

    def test_set_rc_inrange_value_for_block_based_on_pv(self):
        # Arrange
        block_name = "NEW_BLOCK"
        blocks = {block_name: Block(block_name, "", "", "", "")}
        runcontrol = {
            "NEW_BLOCK:RC:LOW.VAL": Block("", "", 10, "", ""),
            "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
            "NEW_BLOCK:SOMETHINGELSE.VAL": Block("", "", False, "", ""),
            "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", ""),
            "NEW_BLOCK:RC:HIGH.VAL": Block("", "", 100, "", ""),
            "NEW_BLOCK:RC:INRANGE.VAL": Block("", "", False, "", ""),
        }

        # Act
        set_rc_values_for_blocks(blocks, runcontrol)

        # Assert
        self.assertEqual(blocks[block_name].get_rc_low(), 10)
        self.assertEqual(blocks[block_name].get_rc_high(), 100)
        self.assertEqual(blocks[block_name].get_rc_inrange(), False)

    def test_set_rc_not_low_value_for_block_based_on_pv(self):
        # Arrange
        block_name = "NEW_BLOCK"
        blocks = {block_name: Block(block_name, "", "", "", "")}
        runcontrol = {
            "NEW_BLOCK:RC:NOTLOW.VAL": Block("", "", 10, "", ""),
            "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
            "NEW_BLOCK:SOMETHINGELSE.VAL": Block("", "", False, "", ""),
            "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", ""),
        }

        # Act
        set_rc_values_for_blocks(blocks, runcontrol)

        # Assert
        self.assertEqual(blocks[block_name].get_rc_low(), None)

    def test_set_rc_values_for_two_blocks_based_on_pv(self):
        # Arrange
        new_block_name = "NEW_BLOCK"
        not_new_block_name = "NOT_NEW_BLOCK"
        blocks = {
            new_block_name: Block(new_block_name, "", "", "", ""),
            not_new_block_name: Block(not_new_block_name, "", "", "", ""),
        }
        runcontrol = {
            "{}:RC:LOW.VAL".format(new_block_name): Block("", "", 10, "", ""),
            "{}:RC:LOW.VAL".format(not_new_block_name): Block("", "", 100, "", ""),
            "{}:SOMETHINGELSE.VAL".format(new_block_name): Block("", "", False, "", ""),
            "{}:RC:LOW.VAL".format("old_block"): Block("", "", 7, "", ""),
        }

        # Act
        set_rc_values_for_blocks(blocks, runcontrol)

        # Assert
        self.assertEqual(blocks[new_block_name].get_rc_low(), 10)
        self.assertEqual(blocks[not_new_block_name].get_rc_low(), 100)

    def test_set_rc_values_for_one_blocks_based_on_pv_leaves_other_unchanged(self):
        # Arrange
        new_block_name = "NEW_BLOCK"
        new_block_rc_low_name = "{}:RC:LOW.VAL".format(new_block_name)
        not_new_block_name = "NOT_NEW_BLOCK"
        blocks = {
            new_block_name: Block(new_block_name, "", "", "", ""),
            not_new_block_name: Block(not_new_block_name, "", "", "", ""),
            "NOT_NEW_BLOCK:VALUE": Block("", "", "", "", ""),
        }
        runcontrol = {new_block_rc_low_name: Block("", "", 10, "", "")}

        # Act
        set_rc_values_for_blocks(blocks, runcontrol)

        # Assert
        self.assertEqual(blocks[new_block_name].get_rc_low(), 10)
        self.assertEqual(blocks[not_new_block_name].get_rc_low(), None)

    def test_set_rc_values_for_leaves_both_unchanged(self):
        # Arrange
        block1_name = "NEW_BLOCK"
        block2_name = "NOT_NEW_BLOCK"
        blocks = {
            block1_name: Block(block1_name, "", "", "", ""),
            block2_name: Block(block2_name, "", "", "", ""),
            "NEW_BLOCK:VALUE": Block("NEW_BLOCK:VALUE", "", "", "", ""),
            "NOT_NEW_BLOCK:VALUE": Block("NOT_NEW_BLOCK:VALUE", "", "", "", ""),
        }

        # Act
        set_rc_values_for_blocks(blocks, {})

        # Assert
        self.assertEqual(blocks[block1_name].get_rc_low(), None)
        self.assertEqual(blocks[block2_name].get_rc_low(), None)

    def test_set_rc_values_with_empty_block_list(self):
        # Act
        try:
            set_rc_values_for_blocks({}, {})
        except Exception:
            self.fail("set_rc_values_for_blocks should handle empty block list")

    def _assert_blocks(self, actual_blocks, expected_blocks):
        # Check blocks are in both
        diff = set(actual_blocks.keys()).difference(set(expected_blocks.keys()))
        self.assertEqual(len(diff), 0, "Extra keys {0}".format(diff))
        diff = set(expected_blocks.keys()).difference(set(actual_blocks.keys()))
        self.assertEqual(len(diff), 0, "Missing keys {0}".format(diff))

        for expected_block_key, expected_block_value in expected_blocks.items():
            actual_block_value = actual_blocks[expected_block_key]
            diff = set(actual_block_value.keys()).difference(set(expected_block_value.keys()))
            self.assertEqual(
                len(diff),
                0,
                "Extra keys in block {block}: {0}".format(diff, block=expected_block_key),
            )
            diff = set(expected_block_value.keys()).difference(set(actual_block_value.keys()))
            self.assertEqual(
                len(diff),
                0,
                "Missing keys in block {block}: {0}".format(diff, block=expected_block_key),
            )

            for (
                expected_block_value_key,
                expected_block_value_value,
            ) in expected_block_value.items():
                actual_block_value_value = actual_block_value[expected_block_value_key]
                self.assertEqual(
                    actual_block_value_value,
                    expected_block_value_value,
                    "Block entry {block}:{key} is different actual {actual} should be {expected}".format(
                        key=expected_block_value_key,
                        block=expected_block_key,
                        actual=actual_block_value_value,
                        expected=expected_block_value_value,
                    ),
                )


class FormatBlockValueTests(unittest.TestCase):
    def test_GIVEN_a_block_with_a_non_numeric_value_WHEN_formatted_with_no_prec_THEN_it_is_returned_unchanged(
        self,
    ):
        value = "this is a string"
        expected_formatted_value = value

        self.assertEqual(format_block_value(value, None), expected_formatted_value)

    def test_GIVEN_a_block_with_a_zero_value_WHEN_formatted_with_prec_3_THEN_it_is_returned_to_3_dp(
        self,
    ):
        value = "0.0"
        expected_formatted_value = "0.000"

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_a_negative_zero_value_WHEN_formatted_to_prec_3_THEN_it_is_returned_to_3_dp(
        self,
    ):
        # Python does have a concept of "-0" so this is a test worth doing.
        value = "-0.0"
        expected_formatted_value = "-0.000"

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_a_medium_size_value_THEN_when_formatted_to_prec_0_THEN_it_is_returned_unchanged(
        self,
    ):
        value = "327"
        expected_formatted_value = value

        self.assertEqual(format_block_value(value, 0), expected_formatted_value)

    def test_GIVEN_a_block_with_a_medium_size_negative_value_WHEN_formatted_to_prec_3_THEN_it_is_returned_to_3_dp(
        self,
    ):
        value = "-327"
        expected_formatted_value = "-327.000"

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_a_small_value_WHEN_formatted_to_prec_3_THEN_it_is_returned_in_exponential_notation_to_3_sf(
        self,
    ):
        value = "0.0000000567"
        expected_formatted_value = "5.67E-08"

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_a_small_negative_value_WHEN_formatted_to_prec_3_THEN_it_is_returned_in_exponential_notation_to_3_sf(
        self,
    ):
        value = "-0.0000000567"
        expected_formatted_value = "-5.67E-08"

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_a_large_value_WHEN_formatted_to_prec_3_THEN_it_is_returned_in_exponential_notation_to_3_sf(
        self,
    ):
        value = "12340000000000000"
        expected_formatted_value = "1.23E+16"

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_a_large_negative_value_WHEN_formatted_to_prec_3_THEN_it_is_returned_in_exponential_notation_to_3_sf(
        self,
    ):
        value = "-12340000000000000"
        expected_formatted_value = "-1.23E+16"

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_a_NAN_value_WHEN_formatted_to_prec_3_THEN_it_is_returned_unchanged(
        self,
    ):
        value = "NAN"
        expected_formatted_value = value

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_a_INF_value_WHEN_formatted_to_prec_3_THEN_it_is_returned_unchanged(
        self,
    ):
        value = "INF"
        expected_formatted_value = value

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_a_negative_INF_value_WHEN_formatted_to_prec_3_THEN_it_is_returned_unchanged(
        self,
    ):
        value = "-INF"
        expected_formatted_value = value

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_a_block_with_an_arbitrary_object_as_its_value_THEN_when_formatted_to_prec_3_it_is_returned_unchanged(
        self,
    ):
        value = object()
        expected_formatted_value = str(value)

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_value_containing_unicode_WHEN_formatting_THEN_original_value_returned_unchanged(
        self,
    ):
        precision = 5
        value = "ƀ Ɓ Ƃ ƃ Ƅ ƅ Ɔ Ƈ ƈ Ɖ Ɗ Ƌ ƌ ƍ Ǝ Ə Ɛ Ƒ ƒ Ɠ Ɣ ƕ Ɩ Ɨ Ƙ ƙ ƚ ƛ Ɯ Ɲ ƞ Ɵ Ơ ơ Ƣ ƣ Ƥ ƥ Ʀ Ƨ ƨ Ʃ ƪ ƫ Ƭ ƭ Ʈ"

        self.assertEqual(format_block_value(value, precision), value)

    def test_GIVEN_a_block_with_a_number_that_does_not_fit_in_a_float_WHEN_formatted_to_prec_3_THEN_it_is_formatted_as_infinity(
        self,
    ):
        value = "5" * 10000
        expected_formatted_value = "INF"

        self.assertEqual(format_block_value(value, 3), expected_formatted_value)

    def test_GIVEN_arbitrary_object_as_precision_WHEN_formatting_THEN_original_value_returned_unchanged(
        self,
    ):
        precision = object()
        value = "12.345"

        self.assertEqual(format_block_value(value, precision), value)

    def test_GIVEN_negative_precision_WHEN_formatting_THEN_original_value_returned_unchanged(self):
        precision = -57
        value = "12.345"

        self.assertEqual(format_block_value(value, precision), value)

    def test_GIVEN_nonsense_precision_WHEN_formatting_THEN_original_value_returned_unchanged(self):
        precision = "this is clearly not a valid precision"
        value = "12.345"

        self.assertEqual(format_block_value(value, precision), value)

    def test_GIVEN_nonsense_precision_containing_unicode_WHEN_formatting_THEN_original_value_returned_unchanged(
        self,
    ):
        precision = "ƀ Ɓ Ƃ ƃ Ƅ ƅ Ɔ Ƈ ƈ Ɖ Ɗ Ƌ ƌ ƍ Ǝ Ə Ɛ Ƒ ƒ Ɠ Ɣ ƕ Ɩ Ɨ Ƙ ƙ ƚ ƛ Ɯ Ɲ ƞ Ɵ Ơ ơ Ƣ ƣ Ƥ ƥ Ʀ Ƨ ƨ Ʃ ƪ ƫ Ƭ ƭ Ʈ"
        value = "12.345"

        self.assertEqual(format_block_value(value, precision), value)


if __name__ == "__main__":
    unittest.main()
