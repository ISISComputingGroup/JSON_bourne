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

import unittest, zlib
from get_webpage import _get_pv_prefix, _set_env, get_instrument_time

INST_LIST_21_11_16 = "789c8bae562a280b284a4dcbac50b25250f2f4b3f2710cf2f50fb252d25150cac82f2ef14bcc4d05c9f8b9444064401" \
                     "2795041a848ad8e0286318e3e6ed8cc000a231b00e262d3ede2eaeb8f4d3b481c593f988fcd004f5fc7106c0680c491" \
                     "0d00f3b119e01beaefe7e68ac50857880cb22150116cc644f9fbfb627307481cd908301fab47823c83b17a04288ee21" \
                     "110bf361600229b82a9"


class CaMock(object):
    def __init__(self):
        self.pvs = dict()

    def get_pv_value(self,pv,asString):
        return self.pvs[pv]

    def set_pv_value(self,pv,value):
        self.pvs[pv] = value


class TestGetWebpage(unittest.TestCase):

    def setUp(self):
        self.environment_variables = dict()

    def tearDown(self):
        pass

    def test_GIVEN_no_environment_variables_WHEN_set_env_called_with_key_and_value_THEN_environment_variables_contains_key_and_value(self):
        # Act
        ca_key = "ca_key"
        ca_ip = "ca_ip"
        _set_env(self.environment_variables,ca_ip,ca_key)

        # Assert
        self.assertEqual(ca_ip,self.environment_variables[ca_key])

    def test_GIVEN_hexed_compressed_sample_inst_list_WHEN_host_name_is_LARMOR_THEN_pv_prefix_is_IN_colon_LARMOR_colon(self):
        # Arrange
        ca = CaMock()
        inst_list_key = "INSTLIST"
        ca.set_pv_value(inst_list_key,INST_LIST_21_11_16)

        # Assert
        self.assertEqual("IN:LARMOR:", _get_pv_prefix("LARMOR", ca, inst_list_key))

    def test_GIVEN_hexed_compressed_sample_inst_list_WHEN_host_name_is_NDXDEMO_THEN_pv_prefix_is_IN_colon_DEMO_colon(self):
        # Arrange
        ca = CaMock()
        inst_list_key = "INSTLIST"
        ca.set_pv_value(inst_list_key,INST_LIST_21_11_16)

        # Assert
        self.assertEqual("IN:DEMO:", _get_pv_prefix("NDXDEMO", ca, inst_list_key))

    def test_GIVEN_hexed_compressed_sample_inst_list_WHEN_host_name_is_NDEMUONFE_THEN_pv_prefix_is_IN_colon_MUONFE_colon(self):
        # Arrange
        ca = CaMock()
        inst_list_key = "INSTLIST"
        ca.set_pv_value(inst_list_key,INST_LIST_21_11_16)

        # Assert
        self.assertEqual("IN:MUONFE:", _get_pv_prefix("NDEMUONFE", ca, inst_list_key))

    def test_GIVEN_hexed_compressed_sample_inst_list_WHEN_host_name_is_unknown_THEN_pv_prefix_has_TE_prefixed(self):
        # Arrange
        ca = CaMock()
        inst_list_key = "INSTLIST"
        ca.set_pv_value(inst_list_key,INST_LIST_21_11_16)

        # Assert
        self.assertEqual("TE:NDW1234:",_get_pv_prefix("NDW1234", ca, inst_list_key))

    def test_GIVEN_unknown_host_name_WHEN_instrument_time_requested_THEN_answer_is_unknown(self):
        self.assertEqual("Unknown",get_instrument_time("NDW1234",CaMock()))

    def test_GIVEN_known_instrument_WHEN_instrument_time_requested_THEN_instrument_time_returned(self):

        # Arrange
        from datetime import datetime as dt
        instrument_time = dt.now()

        ca = CaMock()
        ca.set_pv_value("CS:INSTLIST",INST_LIST_21_11_16)
        ca.set_pv_value("IN:DEMO:CS:IOC:INSTETC_01:DEVIOS:TOD",instrument_time.strftime("%m/%d/%Y %H:%M:%S"))

        # Act/Assert
        self.assertEqual(instrument_time.strftime("%Y/%m/%d %H:%M:%S"),get_instrument_time("DEMO",ca))


if __name__ == '__main__':
    # Run tests
    unittest.main()