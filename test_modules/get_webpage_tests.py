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

import unittest
from lxml import html
from get_webpage import get_instrument_time

INSTRUMENT_TIME = "Inst_time"
URL = ""

def get_html_string(number_of_last_written=1,instrument_time=INSTRUMENT_TIME):

    def instrument_row_html(time):
        return """
        <tr>
            <th>Last Written</th>
            <td>%s</th>
        </tr>
        """ % time

    return """
        <html>
            <body>
                <table>
                    <tbody>
                        <tr>
                            <th>Version</th>
                            <td>3.1.1</th>
                        </tr>
        """ + \
           number_of_last_written*instrument_row_html(instrument_time) + \
        """
                    </tbody>
                </table>
            </body>
        </html>
        """

def get_html_tree(url):
    global URL
    URL = url
    return html.fromstring(get_html_string())

def get_html_tree_with_no_last_written(url):
    return html.fromstring(get_html_string(0))

def get_html_tree_with_multiple_last_written(url):
    return html.fromstring(get_html_string(2))


class TestGetWebpage(unittest.TestCase):

    def test_WHEN_instrument_time_requested_THEN_instrument_time_returned(self):
        self.assertEqual(INSTRUMENT_TIME,get_instrument_time("NDWXXXX",get_html_tree))

    def test_GIVEN_instrument_WHEN_instrument_time_requested_THEN_url_contains_instrument(self):
        instrument_name = "NDWXXXX"
        get_instrument_time(instrument_name,get_html_tree)
        self.assertTrue(instrument_name in URL)

    def test_GIVEN_webpage_with_no_last_written_WHEN_instrument_time_requested_THEN_instrument_time_unknown(self):
        self.assertEqual("Unknown",get_instrument_time("NDWXXXX",get_html_tree_with_no_last_written))

    def test_GIVEN_webpage_with_multiple_last_written_WHEN_instrument_time_requested_THEN_instrument_time_unknown(self):
        self.assertEqual("Unknown",get_instrument_time("NDWXXXX",get_html_tree_with_multiple_last_written))


if __name__ == '__main__':
    # Run tests
    unittest.main()