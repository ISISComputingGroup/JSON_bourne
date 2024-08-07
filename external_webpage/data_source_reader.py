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
Classes for getting external resources.
"""

import json
import logging

import requests
from CaChannel.util import caget

from external_webpage.utils import dehex_and_decompress

logger = logging.getLogger("JSON_bourne")

# Ports for various archiver services
PORT_INSTPV = 4812
PORT_BLOCKS = 4813

# Port for configuration
PORT_CONFIG = 8008

CONFIG_PV = "CS:BLOCKSERVER:GET_CURR_CONFIG_DETAILS"

# Timeout for url get
URL_GET_TIMEOUT = 60


class DataSourceReader(object):
    """
    Access of external data sources from urls.
    """

    def __init__(self, host, pv_prefix):
        """
        Initialize.
        Args:
            host: The host name for the instrument.
        """
        self._host = host
        self._pv_prefix = pv_prefix

    def get_json_from_blocks_archive(self):
        """
        get a list of blocks from the blocks archive

        Returns: list of blocks

        """
        return self._get_json_from_info_page(PORT_BLOCKS, "BLOCKS")

    def get_json_from_dataweb_archive(self):
        """
        get a list of blocks from the dataweb archive

        Returns: list of blocks

        """
        return self._get_json_from_info_page(PORT_BLOCKS, "DATAWEB")

    def get_json_from_instrument_archive(self):
        """
        get a list of blocks from the instrument archive

        Returns: list of blocks

        """
        return self._get_json_from_info_page(PORT_INSTPV, "INST")

    def _get_json_from_info_page(self, port, group_name):
        """
        Read block information from the archiver and populate a list of block objects with it.

        Args:
            port: the port the url is on
            group_name: the name of the group within the archiver to access.

        Returns: A converted list of block objects.

        """
        url = "http://{host}:{port}/group?name={group_name}&format=json".format(
            host=self._host, port=port, group_name=group_name
        )
        try:
            page = requests.get(url, timeout=URL_GET_TIMEOUT)
            return page.json()
        except Exception as e:
            logger.error("URL not found or json not understood: " + str(url))
            raise e

    def read_config(self):
        """
        Read the configuration from the instrument block server. First using channel access then falling back to the
        blockserver webserver.

        Returns: The configuration as a dictionary.
        """
        try:
            pv = self._pv_prefix + CONFIG_PV
            raw = caget(pv, as_string=True)
            config_details = dehex_and_decompress(raw)
            config_details = json.loads(config_details)
            return config_details
        except Exception as ex:
            logger.error(
                f"Error getting instrument config details from {pv}, using webserver instead. {ex}"
            )

        page = requests.get(
            "http://{}:{}/".format(self._host, PORT_CONFIG), timeout=URL_GET_TIMEOUT
        )
        content = page.content.decode("utf-8")
        corrected_page = (
            content.replace("'", '"')
            .replace("None", "null")
            .replace("True", "true")
            .replace("False", "false")
        )
        try:
            return json.loads(corrected_page)
        except Exception as e:
            logger.error("JSON conversion failed: " + str(e))
            logger.error("JSON was: " + str(corrected_page))
            raise e
