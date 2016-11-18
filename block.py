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

from datetime import datetime

class Block:
    """ Class holding Block details. Used for displaying in dataweb"""

    def __init__(self, status, value, alarm, visibility, change_datetime):
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
        self.change_datetime = change_datetime

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

    def get_change_datetime(self):
        """ Returns the datetime of the block's last change"""
        return self.change_datetime

    def set_change_datetime(self,change_datetime):
        self.change_datetime = change_datetime

    def get_description(self):
        """ Returns the full description of this BoolStr object. """
        ans = dict()
        ans["status"] = self.status
        ans["value"] = self.value
        ans["alarm"] = self.alarm
        ans["visibility"] = self.visibility
        ans["changed"] = self.change_datetime
        return ans

    @staticmethod
    def get_from_raw(title, status, block_raw):
        """
        Converts raw block text into a block object

        Args:
            title: The block title
            status: The block status
            block_raw: The raw block string

        Returns: A block object containing the relevant raw information
        """

        def ascii_to_string(ascii):
            string = ''
            for char in ascii:
                if char:
                    string += chr(int(char))
            return string

        def datetime_string_to_datetime(date_and_time_with_nanoseconds):
            return datetime.strptime(date_and_time_with_nanoseconds[:-3], "%Y/%m/%d %H:%M:%S.%f")

        def date_string_and_time_string_to_datetime(date, time_with_nanoseconds):
            return datetime_string_to_datetime(date + " " + time_with_nanoseconds)

        null_date = datetime(1970, 1, 1)
        null_string = "null"

        if block_raw is null_string:
            value = null_string
            alarm = null_string
            change_datetime = null_date
        elif "DAE:STARTTIME.VAL" in title:
            change_datetime_index = 0
            value_index = 1
            alarm_index = 2
            block_split = block_raw.split("\t", 2)
            value = block_split[value_index]
            alarm = block_split[alarm_index]
            change_datetime = datetime_string_to_datetime(block_split[change_datetime_index])
        elif "DAE:TITLE.VAL" in title or "DAE:_USERNAME.VAL" in title:
            # Title and user name are ascii codes spaced by ", "
            change_date_index = 0
            change_time_index = 1
            value_index = 2
            block_split = block_raw.split(None, 2)
            value_ascii = block_split[value_index].split(", ")
            try:
                value = ascii_to_string(value_ascii)
            except Exception as e:
                # Put this here for the moment, title/username need fixing anyway
                value = "Unknown"
            alarm = "null"
            change_datetime = date_string_and_time_string_to_datetime(block_split[change_date_index],
                                                                      block_split[change_time_index])
        else:
            change_date_index = 0
            change_time_index = 1
            value_index = 2
            alarm_index = 3
            block_split = block_raw.split(None, 3)
            value = block_split[value_index]
            alarm = block_split[alarm_index]
            change_datetime = date_string_and_time_string_to_datetime(block_split[change_date_index],
                                                                      block_split[change_time_index])

        return Block(status, value, alarm, True, change_datetime)