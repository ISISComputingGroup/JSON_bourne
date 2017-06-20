import unittest
from block import Block

class TestBlock(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
