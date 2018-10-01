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

import re

from block import Block
from block_utils import shorten_title

from collections import OrderedDict

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
            blocks = OrderedDict()
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

            precision = unicode(current_value.get("Precision", ""))

            value = unicode(current_value["Value"])

            replaced = True
            while replaced:
                value, replaced = self._replace_fake_unicode(value)
            alarm = current_value["Alarm"]
        else:
            value = "null"
            alarm = ""
            units = ""
            precision = 0
        status = Block.CONNECTED if connected else Block.DISCONNECTED

        return Block(name, status, value, alarm, True, precision, units)

    def _replace_fake_unicode(self, value):
        """
        Replace the first `\\udddd` with its unicode equivalent
        Args:
            value: the value to use

        Returns: tuple of new value and whether a replace was made

        """
        # look for \\u-DDD which should be proper unicode characters but are not
        match = re.search(r"((?:\\u[\d-]{4})+)", value)

        if match is None:
            return value, False

        start, end = match.span(1)
        unicode_chars = match.group(1)

        # split multiple unicode characters into values
        string_values = re.split(r"\\u", unicode_chars)[1:]

        # for each value convert to actual value (unsigned byte) and ad to byte array
        asbytearray = bytearray()
        for string_val in string_values:
            val = int(string_val)
            if val < 0:
                val += 256
            asbytearray.append(val)

        # convert byte array to utf8
        asunicode = asbytearray.decode("utf-8")

        # rebuild full string without mistake
        modified_value = value[:start] + asunicode + value[end:]

        return modified_value, True
