import unittest

from mock import Mock
from external_webpage.instrument_information_collator import create_groups_dictionary


class TestInstrumentInformationCollator(unittest.TestCase):

    def test_GIVEN_instrument_config_with_no_groups_WHEN_create_groups_dictionary_called_THEN_return_empty_dict(self):

        instrument_config = Mock()
        instrument_config.groups = []
        result = create_groups_dictionary({}, instrument_config)

        self.assertDictEqual(result, {})

    def test_GIVEN_instrument_config_with_groups_and_no_blocks_WHEN_create_groups_dictionary_called_THEN_return_group_without_blocks(self):

        instrument_config = Mock()
        instrument_config.groups = [{'name': 'test_group', 'blocks': []}]
        result = create_groups_dictionary({}, instrument_config)

        self.assertDictEqual(result, {'test_group': {}})

    def test_GIVEN_instrument_config_with_3_known_groups_WHEN_create_groups_dictionary_called_THEN_return_5_groups(self):

        instrument_config = Mock()
        instrument_config.groups = [{'name': 'test_group_1', 'blocks': []},
                                    {'name': 'test_group_2', 'blocks': []},
                                    {'name': 'test_group_3', 'blocks': []}]
        result = create_groups_dictionary({}, instrument_config)

        self.assertEqual(len(result.keys()), 3)

    def test_GIVEN_block_in_archive_blocks_and_not_instrument_config_WHEN_create_groups_dictionary_called_THEN_return_no_blocks(self):

        instrument_config = Mock()
        instrument_config.groups = []
        archive_block = {'test_block': Mock()}
        result = create_groups_dictionary(archive_block, instrument_config)

        self.assertNotIn('test_block', result)


    def test_GIVEN_block_in_instrument_config_and_not_archive_blocks_WHEN_create_groups_dictionary_called_THEN_return_no_blocks(self):

        instrument_config = Mock()
        instrument_config.groups = [{'name': 'test_group', 'blocks': ['test_block']}]
        result = create_groups_dictionary({}, instrument_config)

        self.assertNotIn('test_block', result)


    def test_GIVEN_block_in_both_instrument_config_and_archive_blocks_WHEN_create_groups_dictionary_called_THEN_return_group_from_instrument_config_with_archive_blocks_data(self):

        instrument_config = Mock()
        instrument_config.groups = [{'name': 'test_group', 'blocks': ['test_block']}]
        archive_block = {'test_block': Mock()}
        result = create_groups_dictionary(archive_block, instrument_config)

        self.assertIn('test_block', result['test_group'])

    def test_GIVEN_ordered_groups_WHEN_create_groups_dictionary_called_THEN_return_same_ordered_groups(self):
        instrument_config = Mock()
        instrument_config.groups = [{'name': 'test_group_1', 'blocks': []},
                                    {'name': 'test_group_2', 'blocks': []},
                                    {'name': 'test_group_3', 'blocks': []}]
        result = create_groups_dictionary({}, instrument_config)

        self.assertTrue(result.keys(), [group['name'] for group in instrument_config.groups])


if __name__ == '__main__':
    unittest.main()
