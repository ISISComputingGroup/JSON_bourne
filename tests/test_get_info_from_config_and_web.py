import os
import sys
from hamcrest import *
import unittest

from mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from external_webpage.instrument_information_collator import InstrumentInformationCollator
from tests.data_mother import ArchiveMother, ConfigMother


class TestGetInfoFromConfigAndWeb(unittest.TestCase):

    def setUp(self):
        self.reader = Mock()
        page_info = ArchiveMother.create_info_page([])
        self.reader.get_json_from_blocks_archive = Mock(return_value=page_info)
        self.reader.get_json_from_dataweb_archive = Mock(return_value=page_info)
        self.reader.get_json_from_instrument_archive = Mock(return_value=page_info)

        config = ConfigMother.create_config()
        self.reader.read_config = Mock(return_value=config)

        self.scraper = InstrumentInformationCollator("host", "prefix", reader=self.reader)

    def test_GIVEN_no_blocks_WHEN_parse_THEN_normal_value_returned(self):
        expected_config_name = "test_config"
        config = ConfigMother.create_config(name=expected_config_name)
        self.reader.read_config = Mock(return_value=config)

        result = self.scraper.collate()

        assert_that(result["config_name"], expected_config_name)

    def test_GIVEN_run_duraction_WHEN_parse_THEN_correctly_formatted_duration_returned(self):
        name = "DAE:RUNDURATION.VAL"
        value = 5025
        units = "s"
        expected_value = "1 hr 23 min 45 s"
        self.reader.get_json_from_instrument_archive = Mock(
            return_value=ArchiveMother.create_info_page([ArchiveMother.create_channel(name=name, value=value, units=units)]))

        result = self.scraper.collate()

        assert_that(result["inst_pvs"]["RUNDURATION"]["value"], is_(expected_value))

    def test_GIVEN_title_is_hidden_WHEN_parse_THEN_title_and_user_appear_us_unavailable(self):
        title_name = "DAE:TITLE.VAL"
        title_value = "a title"
        title_expected_value = InstrumentInformationCollator.PRIVATE_VALUE
        username_name = "DAE:_USERNAME.VAL"
        username_value = "username"
        username_expected_value = InstrumentInformationCollator.PRIVATE_VALUE
        display_name = "DAE:TITLE:DISPLAY.VAL"
        display_value = "No"
        channel_values = [ArchiveMother.create_channel(name=title_name, value=title_value),
                  ArchiveMother.create_channel(name=username_name, value=username_value),
                  ArchiveMother.create_channel(name=display_name, value=display_value)]
        self.reader.get_json_from_instrument_archive = Mock(
            return_value=ArchiveMother.create_info_page(channel_values))

        result = self.scraper.collate()

        assert_that(result["inst_pvs"]["TITLE"]["value"], is_(title_expected_value))
        assert_that(result["inst_pvs"]["_USERNAME"]["value"], is_(username_expected_value))

    def test_GIVEN_title_is_hidden_WHEN_parse_but_no_display_or_username_THEN_no_title_or_username_exist(self):
        display_name = "DAE:TITLE:DISPLAY.VAL"
        display_value = "No"
        channel_values = [ArchiveMother.create_channel(name=display_name, value=display_value)]
        self.reader.get_json_from_instrument_archive = Mock(
            return_value=ArchiveMother.create_info_page(channel_values))

        result = self.scraper.collate()

        assert_that(result["inst_pvs"], not_(has_key("TITLE")))
        assert_that(result["inst_pvs"], not_(has_key("_USERNAME")))

    def test_GIVEN_display_set_to_something_weird_WHEN_parse_THEN_title_and_user_appear_as_unavailable(self):
        title_name = "DAE:TITLE.VAL"
        title_value = "a title"
        title_expected_value = InstrumentInformationCollator.PRIVATE_VALUE
        username_name = "DAE:_USERNAME.VAL"
        username_value = "username"
        username_expected_value = InstrumentInformationCollator.PRIVATE_VALUE
        display_name = "DAE:TITLE:DISPLAY.VAL"
        display_value = "Blah"
        channel_values = [ArchiveMother.create_channel(name=title_name, value=title_value),
                  ArchiveMother.create_channel(name=username_name, value=username_value),
                  ArchiveMother.create_channel(name=display_name, value=display_value)]
        self.reader.get_json_from_instrument_archive = Mock(
            return_value=ArchiveMother.create_info_page(channel_values))

        result = self.scraper.collate()

        assert_that(result["inst_pvs"]["TITLE"]["value"], is_(title_expected_value))
        assert_that(result["inst_pvs"]["_USERNAME"]["value"], is_(username_expected_value))

    def test_GIVEN_display_is_not_present_WHEN_parse_THEN_title_and_user_appear_as_unavailable(self):
        title_name = "DAE:TITLE.VAL"
        title_value = "a title"
        title_expected_value = InstrumentInformationCollator.PRIVATE_VALUE
        username_name = "DAE:_USERNAME.VAL"
        username_value = "username"
        username_expected_value = InstrumentInformationCollator.PRIVATE_VALUE
        channel_values = [ArchiveMother.create_channel(name=title_name, value=title_value),
                  ArchiveMother.create_channel(name=username_name, value=username_value)]
        self.reader.get_json_from_instrument_archive = Mock(
            return_value=ArchiveMother.create_info_page(channel_values))

        result = self.scraper.collate()

        assert_that(result["inst_pvs"]["TITLE"]["value"], is_(title_expected_value))
        assert_that(result["inst_pvs"]["_USERNAME"]["value"], is_(username_expected_value))

    def test_GIVEN_display_is_yes_WHEN_parse_THEN_title_and_user_appear_as_set(self):
        title_name = "DAE:TITLE.VAL"
        title_value = "a title"
        username_name = "DAE:_USERNAME.VAL"
        username_value = "username"
        display_name = "DAE:TITLE:DISPLAY.VAL"
        display_value = "Yes"
        channel_values = [ArchiveMother.create_channel(name=title_name, value=title_value),
                  ArchiveMother.create_channel(name=username_name, value=username_value),
                  ArchiveMother.create_channel(name=display_name, value=display_value)]
        self.reader.get_json_from_instrument_archive = Mock(
            return_value=ArchiveMother.create_info_page(channel_values))

        result = self.scraper.collate()

        assert_that(result["inst_pvs"]["TITLE"]["value"], is_(title_value))
        assert_that(result["inst_pvs"]["_USERNAME"]["value"], is_(username_value))

    def test_GIVEN_displayed_title_as_utf8_characters_in_WHEN_parse_THEN_title_still_has_UTF8_characters_in(self):
        title_name = "DAE:TITLE.VAL"
        title_value = u"a title \u0302"
        display_name = "DAE:TITLE:DISPLAY.VAL"
        display_value = "Yes"
        channel_values = [ArchiveMother.create_channel(name=title_name, value=title_value),
                  ArchiveMother.create_channel(name=display_name, value=display_value)]
        self.reader.get_json_from_instrument_archive = Mock(
            return_value=ArchiveMother.create_info_page(channel_values))

        result = self.scraper.collate()

        assert_that(result["inst_pvs"]["TITLE"]["value"], is_(title_value))

    def test_GIVEN_visible_block_WHEN_parse_THEN_block_is_marked_as_visible(self):

        block_name = "block"
        group_name = "group1"
        expected_is_visible = True
        self.reader.get_json_from_blocks_archive = Mock(
            return_value=ArchiveMother.create_info_page(
                [ArchiveMother.create_channel(name=block_name)]))
        block = ConfigMother.create_block(block_name, is_visibile=expected_is_visible)
        group = ConfigMother.create_group(group_name, [block_name])
        config = ConfigMother.create_config(blocks=[block], groups=[group])
        self.reader.read_config = Mock(return_value=config)

        result = self.scraper.collate()

        assert_that(result["groups"][group_name][block_name]["visibility"], is_(expected_is_visible))

    def test_GIVEN_hidden_block_WHEN_parse_THEN_block_is_marked_as_visible(self):

        block_name = "block"
        group_name = "group1"
        expected_is_visible = False
        self.reader.get_json_from_blocks_archive = Mock(
            return_value=ArchiveMother.create_info_page(
                [ArchiveMother.create_channel(name=block_name)]))
        block = ConfigMother.create_block(block_name, is_visibile=expected_is_visible)
        group = ConfigMother.create_group(group_name, [block_name])
        config = ConfigMother.create_config(blocks=[block], groups=[group])
        self.reader.read_config = Mock(return_value=config)

        result = self.scraper.collate()

        assert_that(result["groups"][group_name][block_name]["visibility"], is_(expected_is_visible))


if __name__ == '__main__':
    unittest.main()
