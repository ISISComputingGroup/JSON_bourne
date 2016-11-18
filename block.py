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

class Block:
    """ Class holding Block details. Used for displaying in dataweb"""

    def __init__(self, status, value, alarm, visibility):
        """
        Standard constructor.

        Args:
            name: the name of the block
            status: the status of the block (e.g disconnected)
            value: the current block value
            alarm: the alarm status
        """

        self.status = status
        self.value = value
        self.alarm = alarm
        self.visibility = visibility

    def get_status(self):
        """ Returns the block status. """
        return self.status

    def set_status(self, status):
        """ Sets the block status. """
        self.status = status

    def get_value(self):
        """ Returns the block value. """
        return self.value

    def set_value(self, value):
        """ Sets the block value. """
        self.value = value

    def get_alarm(self):
        """ Returns the block alarm state. """
        return self.alarm

    def set_alarm(self, alarm):
        """ Sets the block alarm state. """
        self.alarm = alarm

    def get_visibility(self):
        """ Returns the block's visibility """
        return self.visibility

    def set_visibility(self, visibility):
        """ Sets the block's visibility. """
        self.visibility = visibility

    def get_description(self):
        """ Returns the full description of this BoolStr object. """
        ans = dict()
        ans["status"] = self.status
        ans["value"] = self.value
        ans["alarm"] = self.alarm
        ans["visibility"] = self.visibility
        return ans

    @staticmethod
    def from_raw(status, block_raw):
        """
        Converts raw block text into a block object

        Args:
            title: The block title
            status: The block status
            block_raw: The raw block string

        Returns: A block object containing the relevant raw information
        """

        unknown_value = "Unknown"
        null_string = "null"

        # Index in relation to tab separators
        value_index = 1
        alarm_index = 2

        if block_raw in [None, "", "null"]:
            return Block(status, null_string, null_string, True)

        def get_value_from_raw(elements):

            def ascii_to_string(raw_string):
                try:
                    return ''.join(chr(int(c)) for c in raw_string.split(", "))
                except ValueError:
                    return raw_string

            return ascii_to_string(elements[value_index]) if len(elements) > value_index else unknown_value

        def get_alarm_from_raw(elements):
            return elements[alarm_index] if len(elements) > alarm_index else null_string

        tab_split_elements = block_raw.split("\t")
        return Block(status,
                     get_value_from_raw(tab_split_elements),
                     get_alarm_from_raw(tab_split_elements),
                     True)
    