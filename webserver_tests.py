import unittest
from block import Block
from get_block_details import shorten_rc_title, get_rc_values_for_block, get_rc_values_for_block_from_object, set_rc_values_for_block_from_pvs, set_rc_values_for_blocks


class TestWebServer(unittest.TestCase):
    def test_shorten_rc_title_for_default_case(self):
        #Arrange
        test_pv = "TE:NDLT910:DAE:COUNTRATE.VAL"

        #Act
        shortened_title = shorten_rc_title(test_pv)

        #Assert
        self.assertEquals(shortened_title, "COUNTRATE.VAL")

    def test_new_block_rc_in_range(self):
        #Arrange
        test_pv = "TE:NDLT910:CS:SB:NEW_BLOCK:RC:INRANGE.VAL"

        #Act
        shortened_title = shorten_rc_title(test_pv)

        #Assert
        self.assertEquals(shortened_title, "NEW_BLOCK:RC:INRANGE.VAL")

    def test_new_block_rc_enabled(self):
        # Arrange
        test_pv = "TE:NDLT910:CS:SB:NEW_BLOCK:RC:ENABLED.VAL"

        # Act
        shortened_title = shorten_rc_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "NEW_BLOCK:RC:ENABLED.VAL")

    def test_old_block_rc_in_range(self):
        # Arrange
        test_pv = "TE:NDLT910:CS:SB:OLD_BLOCK:RC:INRANGE.VAL"

        # Act
        shortened_title = shorten_rc_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "OLD_BLOCK:RC:INRANGE.VAL")

    def test_random_block_rc_in_range(self):
        # Arrange
        test_pv = "TE:NDLT910:CS:SB:ANY_BLOCK:RC:INRANGE.VAL"

        # Act
        shortened_title = shorten_rc_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "ANY_BLOCK:RC:INRANGE.VAL")

    def test_rc_in_pv_doesnt_count(self):
        # Arrange
        test_pv = "TE:NDLT910:RC.VAL"

        # Act
        shortened_title = shorten_rc_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "RC.VAL")

    def test_larmor_block_high_rc(self):
        # Arrange
        test_pv = "IN:LARMOR:CS:SB:CJHCent:RC:HIGH.VAL"

        # Act
        shortened_title = shorten_rc_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "CJHCent:RC:HIGH.VAL")

    def test_larmor_block_low_rc(self):
        # Arrange
        test_pv = "IN:LARMOR:CS:SB:Chi:RC:LOW.VAL"

        # Act
        shortened_title = shorten_rc_title(test_pv)

        # Assert
        self.assertEquals(shortened_title, "Chi:RC:LOW.VAL")

    def test_get_one_rc_value_for_block(self):
        # Arrange
        test_block = "NEW_BLOCK"
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL" : 10, "MORGAN:RC:LOW.VAL" : 100,  "OLD_BLOCK:RC:LOW.VAL" : 7}

        # Act
        rc_values = get_rc_values_for_block(test_block, test_pvs)

        # Assert
        self.assertEquals(rc_values, 10)

    def test_get_one_rc_value_for_block_with_similar_name(self):
        # Arrange
        test_block = "NEW_BLOCK"
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL": 10, "NOT_NEW_BLOCK:RC:LOW.VAL": 100, "OLD_BLOCK:RC:LOW.VAL": 7}

        # Act
        rc_values = get_rc_values_for_block(test_block, test_pvs)

        # Assert
        self.assertEquals(rc_values, 10)

    def test_get_one_rc_value_for_block_from_object(self):
        # Arrange
        test_block = "NEW_BLOCK"
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL": Block("", "", 10, "", ""),
                    "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
                    "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", "")}

        # Act
        rc_values = get_rc_values_for_block_from_object(test_block, test_pvs)

        # Assert
        self.assertEquals(rc_values, [10])

    def test_get_multiple_rc_value_for_block_from_object_with_similar_name(self):
        # Arrange
        test_block = "NEW_BLOCK"
        test_pvs = {"NEW_BLOCK:RC:LOW.VAL": Block("", "", 10, "", ""),
                    "NEW_BLOCK:RC:HIGH.VAL": Block("", "", 20, "", ""),
                    "NOT_NEW_BLOCK:RC:LOW.VAL": Block("", "", 100, "", ""),
                    "NEW_BLOCK:RC:INRANGE.VAL": Block("", "", False, "", ""),
                    "OLD_BLOCK:RC:LOW.VAL": Block("", "", 7, "", "")}

        # Act
        rc_values = get_rc_values_for_block_from_object(test_block, test_pvs)

        # Assert
        self.assertEquals(set(rc_values), set([10, 20, False]))

    def test_can_set_rc_low_on_a_block(self):
        # Arrange
        test_block = Block("TEST", "", "", "", "")

        # Act
        test_block.set_rc_low(10)

        # Assert
        self.assertEquals(test_block.get_rc_low(), 10)

    def test_can_set_rc_high_on_a_block(self):
        # Arrange
        test_block = Block("TEST", "", "", "", "")

        # Act
        test_block.set_rc_high(100)

        # Assert
        self.assertEquals(test_block.get_rc_high(), 100)

    def test_can_set_rc_inrange_on_a_block(self):
        # Arrange
        test_block = Block("TEST", "", "", "", "")

        # Act
        test_block.set_rc_inrange(False)

        # Assert
        self.assertEquals(test_block.get_rc_inrange(), False)

    def test_when_rc_values_given_block_description_contains_rc_values(self):
        # Arrange
        test_block = Block("TEST", "", "", "", "")
        test_block.set_rc_low(0)
        test_block.set_rc_high(100)
        test_block.set_rc_inrange(False)

        # Act
        description = test_block.get_description()

        # Assert
        self.assertEquals(description["rc_low"], 0)
        self.assertEquals(description["rc_high"], 100)
        self.assertEquals(description["rc_inrange"], False)

    def test_when_rc_values_not_given_block_description_do_not_contain_rc_values(self):
        # Arrange
        test_block = Block("TEST", "", "", "", "")

        # Act
        description = test_block.get_description()

        # Assert
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
        self.assertEquals(test_block.get_rc_low(), '')

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

if __name__ == '__main__':
    unittest.main()
