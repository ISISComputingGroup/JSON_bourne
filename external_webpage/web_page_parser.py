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
Classes for parsing web pages
"""

import logging

from block import Block
from block_utils import shorten_title

logger = logging.getLogger('JSON_bourne')


class BlocksParseError(Exception):
    """
    Exception if there is a problem parsing into blocks.
    """

    def __init__(self, message):
        """
        Initializer.
        Args:
            message: Reason why the input could not be parsed.
        """
        super(BlocksParseError, self).__init__()
        self.message = message


class WebPageParser(object):
    """
    Parses parts of a json web page.
    """

    def extract_blocks(self, info_page_as_json):
        """
        Extract blocks from channels on the given page.
        Args:
            info_page_as_json: the json from an info web page

        Returns: list of blocks

        """

        try:
            blocks = {}
            channels = info_page_as_json["Channels"]
        except (KeyError, TypeError):
            raise BlocksParseError("There is no json object for channels")

        for channel in channels:
            try:
                block = self._create_block_from_channel(channel)
                blocks[block.get_name()] = block
            except (ValueError, KeyError, AttributeError, TypeError) as ex:
                logger.error("Can not convert block from channel {0}: {1}".format(channel, ex))

        return blocks

    def _create_block_from_channel(self, channel):
        """
        Create a single block from a channel object.

        Args:
            channel: the channel.

        Returns:

        """
        name = shorten_title(channel["Channel"])
        connected = channel["Connected"]
        current_value = channel["Current Value"]
        if connected:
            units = current_value.get("Units", "")
            value = current_value["Value"]
            alarm = current_value["Alarm"]
        else:
            value = "null"
            alarm = ""
            units = ""
        status = Block.CONNECTED if connected else Block.DISCONNECTED

        return Block(name, status, value, alarm, True, units)
