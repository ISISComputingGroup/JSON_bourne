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

    def __init__(self, name, status, value, alarm, visibility):
        """
        Standard constructor.

        Args:
            name: the name of the block
            status: the status of the block (e.g disconnected)
            value: the current block value
            alarm: the alarm status
        """
        self.name = name
        self.status = status
        self.value = value
        self.alarm = alarm
        self.visibility = visibility
        self.low = value
        self.high = value
        self.inrange = value

    def get_name(self):
        """ Returns the block status. """
        return self.name

    def set_name(self, name):
        """ Sets the block status. """
        self.status = name

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

    def get_rc_low(self):
        """ Returns the block's low value. """
        return self.low

    def set_rc_low(self, value):
        """ Sets the block's low value. """
        self.low = value

    def get_rc_high(self):
        """ Returns the block's high value. """
        return self.high

    def set_rc_high(self, value):
        """ Sets the block's high value. """
        self.high = value

    def get_rc_inrange(self):
        """ Returns the block's inrange status. """
        return self.inrange

    def set_rc_inrange(self, value):
        """ Sets the block's inrange status. """
        self.inrange = value

    def is_connected(self):
        """
        :return Whether this block is connected
        """
        return self.status == "Connected"

    def get_description(self):
        """ Returns the full description of this BoolStr object. """
        ans = {}
        ans["status"] = self.status
        ans["value"] = self.value
        if self.low != "":
            ans["rc_low"] = self.low

        if self.high != "":
            ans["rc_high"] = self.high

        if self.inrange != "":
            ans["rc_inrange"] = self.inrange

        ans["alarm"] = self.alarm
        ans["visibility"] = self.visibility
        return ans

    def __str__(self):
        return self.get_description().__str__()
