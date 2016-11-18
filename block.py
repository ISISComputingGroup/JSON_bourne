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

    def __init__(self, status, value, alarm, visibility, update_datetime):
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
        self.update_datetime = update_datetime

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

    def get_update_datetime(self):
        """ Returns the datetime of the block's last change"""
        return self.update_datetime

    def set_update_datetime(self, change_datetime):
        self.update_datetime = change_datetime

    def get_description(self):
        """ Returns the full description of this BoolStr object. """
        ans = dict()
        ans["status"] = self.status
        ans["value"] = self.value
        ans["alarm"] = self.alarm
        ans["visibility"] = self.visibility
        ans["updated"] = self.update_datetime
        return ans

    @staticmethod
    def from_raw(title, status, block_raw):
        """
        Converts raw block text into a block object

        Args:
            title: The block title
            status: The block status
            block_raw: The raw block string

        Returns: A block object containing the relevant raw information
        """

        unknown_value = "Unknown"
        unknown_alarm = unknown_value
        null_date = datetime(1970, 1, 1)
        null_string = "null"

        if block_raw in [None, "","null"]:
            return Block(null_string,null_string,null_string,True,null_date)

        def title_is_for_hexed_values(t):
            return any([hexed_title in t for hexed_title in ["DAE:TITLE.VAL","DAE:_USERNAME.VAL"]])

        def title_is_for_start_time(t):
            return "DAE:STARTTIME.VAL" in t

        def get_value_from_raw(raw, block_title):

            def ascii_chars_to_string(ascii):
                try:
                    return ''.join(chr(int(c)) for c in ascii)
                except ValueError as e:
                    return unknown_value

            try:
                value_index = 2
                if title_is_for_hexed_values(block_title):
                    block_value = ascii_chars_to_string(raw.split(None,value_index)[value_index].split(", "))
                elif title_is_for_start_time(block_title):
                    number_of_elements = 3
                    block_value = " ".join(raw.replace("\t", " ").
                                           split(" ")[value_index:value_index+number_of_elements])
                else:
                    block_value = raw.split(" ")[value_index]
            except:
                block_value = unknown_value
            return block_value

        def get_alarm_from_raw(raw, block_title):
            try:
                if title_is_for_hexed_values(block_title):
                    block_alarm = null_string
                elif title_is_for_start_time(block_title):
                    block_index = 5
                    block_alarm = raw.replace("\t", " ").split(" ")[block_index].split(",")[0]
                else:
                    block_index = 3
                    block_alarm = raw.split(" ")[block_index]
            except:
                block_alarm = unknown_alarm
            return block_alarm

        def get_datetime_from_raw(raw):
            try:
                words = raw.replace("\t"," ").split(" ")
                date_index = 0
                time_index = 1
                number_of_nanosecond_characters = 3
                return datetime.strptime(words[date_index] + " " + words[time_index][:-number_of_nanosecond_characters],
                                         "%Y/%m/%d %H:%M:%S.%f")
            except:
                return null_date

        return Block(status,
                     get_value_from_raw(block_raw,title),
                     get_alarm_from_raw(block_raw,title),
                     True,
                     get_datetime_from_raw(block_raw))