# This file is part of the ISIS IBEX application.
# Copyright (C) 2017 Science & Technology Facilities Council.
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
"""
Classes getting external resources from an instrument and formating them for the info page.
"""

import logging
from builtins import object, str
from collections import OrderedDict

from block_utils import format_blocks, set_rc_values_for_blocks
from external_webpage.data_source_reader import DataSourceReader
from external_webpage.web_page_parser import WebPageParser

logger = logging.getLogger('JSON_bourne')


def create_groups_dictionary(archive_blocks, instrument_config):
    """
    Populate groups with block information from the archive server.
    Args:
        archive_blocks (dict[str, block.Block]): Block information from the archive server.
        instrument_config (InstrumentConfig): Instrument configurations from the block server.

    Returns:
        groups (dict[str, dict[str, dict]]): All groups and their associated blocks.

    """
    blocks_all_formatted = format_blocks(archive_blocks)
    groups = OrderedDict()
    for group in instrument_config.groups:
        blocks = OrderedDict()
        for block in group["blocks"]:
            if block in blocks_all_formatted.keys():
                blocks[block] = blocks_all_formatted[block]
        groups[group["name"]] = blocks
    return groups


class InstrumentConfig(object):
    """
    The instrument configuration.
    """

    def __init__(self, config_json):
        """
        Initialize.
        Args:
            config_json: The json dictionary from which to create the configuration
        """
        self._config = config_json
        self.groups = self._config["groups"]
        self.name = self._config["name"]

        self.blocks = OrderedDict()
        for block in self._config["blocks"]:
            self.blocks[block["name"]] = block

    def block_is_visible(self, block_name):
        """
        According to the configuration is a block visible to the user. If it is not in the configuration assume it
        should be visible
        Args:
            block_name: Block name to query

        Returns: True if it is visible; False otherwise
        Raises KeyError: If the block does not exist.

        """
        try:
            block = self.blocks[block_name]
            return block["visible"]
        except KeyError:
            return True


class InstrumentInformationCollator(object):
    """
    Collect instrument information and summarise as a dictionary.
    """

    # String to use for title and username if they are private
    PRIVATE_VALUE = "Hidden"
    # Name of the username channel
    USERNAME_CHANNEL_NAME = "_USERNAME"
    # name of the title channel
    TITLE_CHANNEL_NAME = "TITLE"
    # name of the channel which determins of the username and title should be displayed
    DISPLAY_TITLE_CHANNEL_NAME = "DISPLAY"
    # name of the channel of the current run duration
    RUN_DURATION_CHANNEL_NAME = "RUNDURATION"
    # name of the channel fo the run duration for the current period
    RUN_DURATION_PD_CHANNEL_NAME = "RUNDURATION_PD"

    def __init__(self, host, pv_prefix, reader=None):
        """
        Initialize.
        Args:
            host: The host of the instrument from which to read the information.
            pv_prefix: The pv_prefix of the instrument from which to read the information.
            reader: A reader object to get external information.
        """
        if reader is None:
            self.reader = DataSourceReader(host, pv_prefix)
        else:
            self.reader = reader

        self.web_page_parser = WebPageParser()

    def _get_inst_pvs(self, instrument_archive_blocks):
        """
        Extracts and formats a list of relevant instrument PVs from all instrument PVs.

        Args:
            instrument_archive_blocks: List of blocks from the instrument archive.

        Returns: A trimmed list of instrument PVs.

        """
        wanted = {}

        title_channel_name = InstrumentInformationCollator.TITLE_CHANNEL_NAME
        username_channel_name = InstrumentInformationCollator.USERNAME_CHANNEL_NAME
        run_duration_channel_name = InstrumentInformationCollator.RUN_DURATION_CHANNEL_NAME
        run_duration_pd_channel_name = InstrumentInformationCollator.RUN_DURATION_PD_CHANNEL_NAME
        required_pvs = ["RUNSTATE", "RUNNUMBER", "_RBNUMBER", title_channel_name,
                        username_channel_name, "STARTTIME",
                        run_duration_channel_name, run_duration_pd_channel_name, "GOODFRAMES", "GOODFRAMES_PD",
                        "RAWFRAMES", "RAWFRAMES_PD", "PERIOD", "NUMPERIODS", "PERIODSEQ", "BEAMCURRENT", "TOTALUAMPS",
                        "COUNTRATE", "DAEMEMORYUSED", "TOTALCOUNTS", "DAETIMINGSOURCE", "MONITORCOUNTS",
                        "MONITORSPECTRUM", "MONITORFROM", "MONITORTO", "NUMTIMECHANNELS", "NUMSPECTRA", "SHUTTER",
                        "SIM_MODE", "BANNER:RIGHT:LABEL", "BANNER:MIDDLE:LABEL", "BANNER:LEFT:LABEL",
                        "1:1:LABEL", "2:1:LABEL", "3:1:LABEL", "1:2:LABEL", "2:2:LABEL", "3:2:LABEL",
                        "BANNER:LEFT:LABEL", "BANNER:MIDDLE:LABEL", "BANNER:RIGHT:LABEL", "1:1:VALUE", "2:1:VALUE",
                        "3:1:VALUE", "1:2:VALUE", "2:2:VALUE", "3:2:VALUE", "BANNER:LEFT:VALUE",
                        "BANNER:MIDDLE:VALUE", "BANNER:RIGHT:VALUE", "TIME_OF_DAY"]


        for pv in required_pvs:
            if pv + ".VAL" in instrument_archive_blocks:
                wanted[pv] = instrument_archive_blocks[pv + ".VAL"]

        try:
            self._convert_seconds(wanted[run_duration_channel_name])
        except KeyError:
            pass

        try:
            self._convert_seconds(wanted[run_duration_pd_channel_name])
        except KeyError:
            pass

        display_title_channel_name = InstrumentInformationCollator.DISPLAY_TITLE_CHANNEL_NAME + ".VAL"
        if display_title_channel_name not in instrument_archive_blocks or \
                instrument_archive_blocks[display_title_channel_name].get_value().lower() != "yes":
            if title_channel_name in wanted:
                wanted[title_channel_name].set_value(InstrumentInformationCollator.PRIVATE_VALUE)
            if username_channel_name in wanted:
                wanted[username_channel_name].set_value(InstrumentInformationCollator.PRIVATE_VALUE)

        return wanted

    def _convert_seconds(self, block):
        """
        Receives the value from the block and converts to hours, minutes and seconds.

        Args:
            block: the block to convert

        """
        if not block.is_connected():
            return
        old_value = block.get_value()
        minutes, seconds = divmod(int(old_value), 60)
        hours, minutes = divmod(minutes, 60)

        if hours == 0 and minutes == 0:
            block.set_value("{} s".format(old_value))
        elif hours == 0:
            block.set_value("{} min {} s".format(str(minutes), str(seconds)))
        else:
            block.set_value("{} hr {} min {} s".format(str(hours), str(minutes), str(seconds)))
        block.set_units("")

    def collate(self):
        """
        Returns the collated information on instrument configuration, blocks and run status PVs as JSON.

        Returns: JSON of the instrument's configuration and status.

        """
        instrument_config = InstrumentConfig(self.reader.read_config())
        error_statuses = []

        try:
            # read blocks
            json_from_blocks_archive = self.reader.get_json_from_blocks_archive()
            blocks = self.web_page_parser.extract_blocks(json_from_blocks_archive)

            json_from_dataweb_archive = self.reader.get_json_from_dataweb_archive()
            dataweb_blocks = self.web_page_parser.extract_blocks(json_from_dataweb_archive)

        except Exception as e:
            error_string = "Failed to read block archiver"
            error_statuses.append(error_string)
            logger.error(f"{error_string}: " + str(e))
            blocks = {}
            dataweb_blocks = {}
        
        try:
            json_from_instrument_archive = self.reader.get_json_from_instrument_archive()
            instrument_blocks = self.web_page_parser.extract_blocks(json_from_instrument_archive)

            inst_pvs = format_blocks(self._get_inst_pvs(instrument_blocks))
        except Exception as e:
            error_string = "Failed to read instrument archiver"
            error_statuses.append(error_string)
            logger.error(f"{error_string}: " + str(e))
            inst_pvs = {}

        try:
            set_rc_values_for_blocks(blocks, dataweb_blocks)
        except Exception as e:
            logger.error("Error in setting rc values for blocks: " + str(e))

        # get block visibility from config
        for block_name, block in blocks.items():
            block.set_visibility(instrument_config.block_is_visible(block_name))

        groups = create_groups_dictionary(blocks, instrument_config)

        return {
            "config_name": instrument_config.name,
            "groups": groups,
            "inst_pvs": inst_pvs,
            "error_statuses": error_statuses
        }
