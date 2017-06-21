import unittest
from block import Block
from block_utils import (format_blocks, set_rc_values_for_block_from_pvs,
        set_rc_values_for_blocks, shorten_title)


class TestBlockUtils(unittest.TestCase):

    def test_format_blocks_with_two_blocks(self):
        #Arrange
        test_blocks = {
            "NEW_BLOCK": Block("NEW_BLOCK", "INVALID", 10, "UDF_ALARM", False), 
            "NOT_NEW_BLOCK": Block("NOT_NEW_BLOCK", "GOOD", 100, "NO_ALARM", False)
        }
        expected_result = {
            'NEW_BLOCK': {'status': 'INVALID', 'alarm': 'UDF_ALARM',
                'visibility': False, 'value': 10, 'rc_enabled': 'NO'}, 
            'NOT_NEW_BLOCK': {'status': 'GOOD', 'alarm': 'NO_ALARM',
                'visibility': False, 'value': 100, 'rc_enabled': 'NO'}
        }

        #Act
        formatted_blocks = format_blocks(test_blocks)

        #Assert
        self.assertEquals(formatted_blocks, expected_result)

    def test_format_blocks_with_one_block(self):
        #Arrange
        test_blocks = {
            "NEW_BLOCK": Block("NEW_BLOCK", "", 10, "", False)
        }
        expected_result = {
            'NEW_BLOCK': {'status': '', 'alarm': '', 'visibility': False,
                'value': 10, 'rc_enabled': 'NO'}, 
        }

        #Act
        formatted_blocks = format_blocks(test_blocks)

        #Assert
        self.assertEquals(formatted_blocks, expected_result)

    def test_format_blocks_with_one_block_with_rc_values(self):
        #Arrange
        block = Block("NEW_BLOCK", "", 10, "", False)
        block.set_rc_low(0)
        block.set_rc_high(100)
        block.set_rc_inrange(False)
        block.set_rc_enabled("YES")

        test_blocks = {
            "NEW_BLOCK": block
        }
        expected_result = {
            'NEW_BLOCK': {'status': '', 'alarm': '', 'visibility': False,
                'value': 10, 'rc_high': 100, 'rc_low': 0, 'rc_inrange': False,
                'rc_enabled': 'YES'}, 
        }

        #Act
        formatted_blocks = format_blocks(test_blocks)

        #Assert
        self.assertEquals(formatted_blocks, expected_result)

    def test_format_blocks_with_two_blocks_with_rc_values(self):
        #Arrange
        block1 = Block("NEW_BLOCK", "", 10, "", False)
        block1.set_rc_low(10)
        block1.set_rc_high(20)
        block1.set_rc_inrange(True)
        block1.set_rc_enabled("YES")

        block2 = Block("OLD_BLOCK", "", 10, "", False)
        block2.set_rc_low(0)
        block2.set_rc_high(100)
        block2.set_rc_inrange(False)

        test_blocks = {
                "NEW_BLOCK": block1, "OLD_BLOCK": block2
        }
        expected_result = {
            'NEW_BLOCK': {'status': '', 'alarm': '', 'visibility': False,
                'value': 10, 'rc_high': 20, 'rc_low': 10, 'rc_inrange': True,
                'rc_enabled': 'YES'}, 
            'OLD_BLOCK': {'status': '', 'alarm': '', 'visibility': False,
                'value': 10, 'rc_high': 100, 'rc_low': 0, 'rc_inrange': False,
                'rc_enabled': 'NO'}, 
        }

        #Act
        formatted_blocks = format_blocks(test_blocks)

        #Assert
        self.assertEquals(formatted_blocks, expected_result)

    def test_format_blocks_with_empty_dict(self):
        #Arrange
        test_blocks = {}
        expected_result = {}

        #Act
        formatted_blocks = format_blocks(test_blocks)

        #Assert
        self.assertEquals(formatted_blocks, expected_result)

    def test_shorten_title_for_default_case(self):
        #Arrange
        test_pv = "TE:NDLT910:DAE:COUNTRATE.VAL"

        #Act
        shortened_title = shorten_title(test_pv)

        #Assert
        self.assertEquals(shortened_title, "COUNTRATE.VAL")

    def test_shorten_title_with_rc_in_range(self):
        #Arrange
        test_pv = "TE:NDLT910:CS:SB:NEW_BLOCK:RC:INRANGE.VAL"

        #Act
        shortened_title = shorten_title(test_pv)

        #Assert
        self.assertEquals(shortened_title, "NEW_BLOCK:RC:INRANGE.VAL")

    def test_shorten_title_with_rc_enabled(self):
        # Arrange
        test_pv = "TE:NDLT910:CS:SB:NEW_BLOCK:RC:ENABLED.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "NEW_BLOCK:RC:ENABLED.VAL")

    def test_shorten_title_with_rc_in_range(self):
        # Arrange
        test_pv = "TE:NDLT910:CS:SB:OLD_BLOCK:RC:INRANGE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "OLD_BLOCK:RC:INRANGE.VAL")

    def test_shorten_title_with_empty_string(self):
        # Arrange
        test_pv = ""

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "")

    def test_shorten_title_with_bad_rc_value(self):
        # Arrange
        test_pv = "OLD_BLOCK:RC:OUTRANGE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "OUTRANGE.VAL")

    def test_shorten_title_with_malformed_input_end_of_title(self):
        # Arrange
        test_pv = "INRANGE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "INRANGE.VAL")

    def test_shorten_title_with_malformed_input_rc_value(self):
        # Arrange
        test_pv = "RC:INRANGE.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "RC:INRANGE.VAL")

    def test_shorten_title_rc_in_pv_doesnt_count(self):
        # Arrange
        test_pv = "TE:NDLT910:RC.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "RC.VAL")

    def test_shorten_title_larmor_block_high_rc(self):
        # Arrange
        test_pv = "IN:LARMOR:CS:SB:CJHCent:RC:HIGH.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "CJHCent:RC:HIGH.VAL")

    def test_shorten_title_larmor_block_low_rc(self):
        # Arrange
        test_pv = "IN:LARMOR:CS:SB:Chi:RC:LOW.VAL"

        # Act
        shortened_title = shorten_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "Chi:RC:LOW.VAL")

    def test_when_rc_values_given_block_description_contains_rc_values(self):
        # Arrange
        test_block = Block("TEST", "INVALID", "10", "UDF_ALARM", "OFF")
        test_block.set_rc_low(0)
        test_block.set_rc_high(100)
        test_block.set_rc_inrange(False)

        # Act
        description = test_block.get_description()

        # Assert
        self.assertEquals(description["visibility"], "OFF")
        self.assertEquals(description["status"], "INVALID")
        self.assertEquals(description["alarm"], "UDF_ALARM")
        self.assertEquals(description["rc_low"], 0)
        self.assertEquals(description["rc_high"], 100)
        self.assertEquals(description["rc_inrange"], False)

    def test_when_rc_values_not_given_block_description_do_not_contain_rc_values(self):
        # Arrange
        test_block = Block("TEST", "INVALID", "10", "UDF_ALARM", "OFF")

        # Act
        description = test_block.get_description()

        # Assert
        self.assertEquals(description["visibility"], "OFF")
        self.assertEquals(description["status"], "INVALID")
        self.assertEquals(description["alarm"], "UDF_ALARM")
        self.assertTrue("rc_low" not in description)
        self.assertTrue("rc_high" not in description)
        self.assertTrue("rc_inrange" not in description)

    def test_set_rc_low_value_for_block_based_on_pv(self):
        # Arrange
        test_block = Block("NEW_BLOCK", "", "", "", "")
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL": Block("", "", 10, "", ""),
                    "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
                    "NEW_BLOCK:SOMETHINGELSE.VAL": Block("", "", False, "", ""),
                    "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", "")}

        # Act
        set_rc_values_for_block_from_pvs(test_block, test_pvs)

        # Assert
        self.assertEquals(test_block.get_rc_low(), 10)

    def test_set_rc_high_value_for_block_based_on_pv(self):
        # Arrange
        test_block = Block("NEW_BLOCK", "", "", "", "")
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL": Block("", "", 10, "", ""),
                    "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
                    "NEW_BLOCK:SOMETHINGELSE.VAL": Block("", "", False, "", ""),
                    "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", ""),
                    "NEW_BLOCK:RC:HIGH.VAL": Block("", "", 100, "", "")}

        # Act
        set_rc_values_for_block_from_pvs(test_block, test_pvs)

        # Assert
        self.assertEquals(test_block.get_rc_low(), 10)
        self.assertEquals(test_block.get_rc_high(), 100)

    def test_set_rc_inrange_value_for_block_based_on_pv(self):
        # Arrange
        test_block = Block("NEW_BLOCK", "", "", "", "")
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL": Block("", "", 10, "", ""),
                    "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
                    "NEW_BLOCK:SOMETHINGELSE.VAL": Block("", "", False, "", ""),
                    "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", ""),
                    "NEW_BLOCK:RC:HIGH.VAL": Block("", "", 100, "", ""),
                    "NEW_BLOCK:RC:INRANGE.VAL": Block("", "", False, "", "")}

        # Act
        set_rc_values_for_block_from_pvs(test_block, test_pvs)

        # Assert
        self.assertEquals(test_block.get_rc_low(), 10)
        self.assertEquals(test_block.get_rc_high(), 100)
        self.assertEquals(test_block.get_rc_inrange(), False)

    def test_set_rc_not_low_value_for_block_based_on_pv(self):
        # Arrange
        test_block = Block("NEW_BLOCK", "", "", "", "")
        test_pvs = {"NEW_BLOCK:RC:NOTLOW.VAL": Block("", "", 10, "", ""),
                    "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
                    "NEW_BLOCK:SOMETHINGELSE.VAL": Block("", "", False, "", ""),
                    "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", "")}

        # Act
        set_rc_values_for_block_from_pvs(test_block, test_pvs)

        # Assert
        self.assertEquals(test_block.get_rc_low(), None)

    def test_set_rc_values_for_two_blocks_based_on_pv(self):
        # Arrange
        test_blocks = [Block("NEW_BLOCK", "", "", "", ""),Block("NOT_NEW_BLOCK", "", "", "", "")]
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL": Block("", "", 10, "", ""),
                    "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
                    "NEW_BLOCK:SOMETHINGELSE.VAL": Block("", "", False, "", ""),
                    "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", "")}

        # Act
        set_rc_values_for_blocks(test_blocks, test_pvs)

        # Assert
        self.assertEquals(test_blocks[0].get_rc_low(), 10)
        self.assertEquals(test_blocks[1].get_rc_low(), 100)

    def test_set_rc_values_for_one_blocks_based_on_pv_leaves_other_unchanged(self):
        # Arrange
        test_blocks = [Block("NEW_BLOCK", "", "", "", ""),Block("NOT_NEW_BLOCK", "", "", "", "")]
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL": Block("", "", 10, "", ""),
                    "NOT_NEW_BLOCK:VALUE": Block("", "", "", "", "")}

        # Act
        set_rc_values_for_blocks(test_blocks, test_pvs)

        # Assert
        self.assertEquals(test_blocks[0].get_rc_low(), 10)
        self.assertEquals(test_blocks[1].get_rc_low(), None)

    def test_set_rc_values_for_leaves_both_unchanged(self):
        # Arrange
        test_blocks = [Block("NEW_BLOCK", "", "", "", ""),Block("NOT_NEW_BLOCK", "", "", "", "")]
        test_pvs = {"NEW_BLOCK:VALUE": Block("", "", "", "", ""),
                    "NOT_NEW_BLOCK:VALUE": Block("", "", "", "", "")}

        # Act
        set_rc_values_for_blocks(test_blocks, test_pvs)

        # Assert
        self.assertEquals(test_blocks[0].get_rc_low(), None)
        self.assertEquals(test_blocks[1].get_rc_low(), None)

    def test_set_rc_values_with_empty_block_list(self):
        # Arrange
        test_blocks = []
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL": Block("", "", 10, "", ""),
                    "NOT_NEW_BLOCK:VALUE": Block("", "", "", "", "")}

        # Act
        try:
            set_rc_values_for_blocks(test_blocks, test_pvs)
        except Exception, e:
            self.fail("set_rc_values_for_blocks should handle empty block list")

    def test_set_rc_values_with_empty_pv_list(self):
        # Arrange
        test_blocks = [Block("NEW_BLOCK", "", "", "", ""),Block("NOT_NEW_BLOCK", "", "", "", "")]
        test_pvs = {}

        # Act
        try:
            set_rc_values_for_blocks(test_blocks, test_pvs)
        except Exception, e:
            self.fail("set_rc_values_for_blocks should handle empty pv list")


if __name__ == '__main__':
    unittest.main()
