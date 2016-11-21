from lxml import html
import requests
import json
from block import Block
from datetime import datetime
import logging
import zlib
import os
import ast
from genie_python.genie_cachannel_wrapper import CaChannelWrapper


PORT_INSTPV = 4812
PORT_BLOCKS = 4813
PORT_CONFIG = 8008


def shorten_title(title):
    """
    Gets a PV title by shortening its address to the last segment.

    Args:
        title: The PV address as string.

    Returns: The last segment of the input PV address as string.

    """
    number = title.rfind(':')
    return title[number + 1:]


def get_info(url):
    """
    Reads block information from a url and populates a list of block objects with it.

    Args:
        url: The block information source.

    Returns: A converted list of block objects.

    """
    try:
        page = requests.get(url)
    except Exception as e:
        logging.error("URL not found: " + str(url))
        raise e

    tree = html.fromstring(page.content)

    titles = tree.xpath("//tr/th/a")
    titles = [t.text for t in titles]

    status = tree.xpath("//table[2]/tbody/tr/td[1]")
    status_text = list()
    for s in status:
        if s.text is None:
            # This means there is an extra <font> in the XML to change the colour of the value
            # This only happens when the PV is "Disconnected"
            # This assumption speeds up the program significantly
            status_text.append("Disconnected")
        else:
            status_text.append(s.text)

    info = tree.xpath("//table[2]/tbody/tr/td[3]")

    return {shorten_title(titles[i]): Block.from_raw(status_text[i], info[i].text) for i in range(len(titles))}


def get_instpvs(url):
    """
    Extracts and formats a list of relevant instrument PVs from all instrument PVs.

    Args:
        url: The source of the instrument PV information.

    Returns: A trimmed list of instrument PVs.

    """
    wanted = dict()
    ans = get_info(url)

    required_pvs = ["RUNSTATE", "RUNNUMBER", "_RBNUMBER", "TITLE", "DISPLAY", "_USERNAME", "STARTTIME",
                    "RUNDURATION", "RUNDURATION_PD", "GOODFRAMES", "GOODFRAMES_PD", "RAWFRAMES", "RAWFRAMES_PD",
                    "PERIOD", "NUMPERIODS", "PERIODSEQ", "BEAMCURRENT", "TOTALUAMPS", "COUNTRATE", "DAEMEMORYUSED",
                    "TOTALCOUNTS", "DAETIMINGSOURCE", "MONITORCOUNTS", "MONITORSPECTRUM", "MONITORFROM", "MONITORTO",
                    "NUMTIMECHANNELS", "NUMSPECTRA"]

    for pv in required_pvs:
        if pv + ".VAL" in ans:
            wanted[pv] = ans[pv + ".VAL"]

    return wanted


def scrape_webpage(host="localhost"):
    """
    Returns the collated information on instrument configuration, blocks and run status PVs as JSON.
    
    
    Args:
        host: The target instrument.

    Returns: JSON of the instrument's configuration and status.

    """

    # read config
    page = requests.get('http://%s:%s/' % (host, PORT_CONFIG))
    corrected_page = page.content.replace("'", '"').replace("None", "null").replace("True", "true").replace("False", "false")
    
    try:
        config = json.loads(corrected_page)
    except Exception as e:
        logging.error("JSON conversion failed: " + str(e))
        logging.error("JSON was: " + str(config))
        raise e
        
    block_vis = get_block_visibility(config)

    # read blocks
    blocks_log = get_info('http://%s:%s/group?name=BLOCKS' % (host, PORT_BLOCKS))
    blocks_nolog = get_info('http://%s:%s/group?name=DATAWEB' % (host, PORT_BLOCKS))
    blocks_all = dict(blocks_log.items() + blocks_nolog.items())

    # get block visibility from config
    for block in blocks_all:
        blocks_all[block].set_visibility(block_vis.get(block))

    blocks_all_formatted = format_blocks(blocks_all)

    groups = dict()
    for group in config["groups"]:
        blocks = dict()
        for block in group["blocks"]:
            if block in blocks_all_formatted.keys():
                blocks[block] = blocks_all_formatted[block]
        groups[group["name"]] = blocks

    try:
        output = dict()
        output["config_name"] = config["name"]
        output["groups"] = groups
        output["inst_pvs"] = format_blocks(get_instpvs('http://%s:%s/group?name=INST' % (host, PORT_INSTPV)))
        output["instrument_time"] = get_instrument_time(host)
    except Exception as e:
        logging.error("Output construction failed " + str(e))
        raise e

    return output


def _set_env(environment_variables=os.environ, epics_ca_ip="127.255.255.255 130.246.51.255",
             epics_ca_key="EPICS_CA_ADDR_LIST"):
    """
    If we're not in an EPICS terminal, add the address list to the set of
    environment keys.

    Args:
        environment_variables: The current list of Python environment variables
        epics_ca_ip: The IP address for EPICS channel access
        epics_ca_key: The name of the environment variable for the channel access ip

    """
    if epics_ca_key not in environment_variables.keys():
        environment_variables[epics_ca_key] = epics_ca_ip


def _get_pv_prefix(host_instrument, channel_access, inst_list_pv="CS:INSTLIST"):
    """
    Get the PV prefix for a specified host instrument

    Args:
        host_instrument: The name of the instrument whose PV prefix we want
        channel_access: Library to access PVs via channel access. Must support get_pv_value
        inst_list_pv: The PV of the instrument list

    Return:
        string: PV prefix for the instrument
    """
    try:
        instruments_list = ast.literal_eval(zlib.decompress(channel_access.
                                                            get_pv_value(inst_list_pv,True).decode("hex")))
    except Exception as e:
        logging.error("Unable to get PV prefix: " + e.message)
        return None

    pv_prefix = None
    for instrument_dict in instruments_list:
        if instrument_dict["name"].upper() == host_instrument.upper() or \
                        instrument_dict["hostName"].upper() == host_instrument.upper():
            pv_prefix = instrument_dict["pvPrefix"]
            break

    return pv_prefix


def get_instrument_time(host_instrument, ca=CaChannelWrapper):
    """
    Gets the instrument time from a specific host instrument via channel access

    Args:
        host_instrument: The name of the host instrument

    Returns: The instrument time as a string

    """

    unable_to_determine_instrument_time = "Unknown"
    incoming_datetime_format = "%m/%d/%Y %H:%M:%S"
    desired_datetime_format = "%Y/%m/%d %H:%M:%S"

    _set_env()
    pv_prefix = _get_pv_prefix(host_instrument, ca)
    if pv_prefix is None:
        return unable_to_determine_instrument_time

    try:
        instrument_datetime = datetime.strptime(ca.get_pv_value(pv_prefix+"CS:IOC:INSTETC_01:DEVIOS:TOD",True),
                                                incoming_datetime_format)
    except Exception as e:
        logging.error("Unable to generate instrument time: " + e.message)
        return unable_to_determine_instrument_time

    return instrument_datetime.strftime(desired_datetime_format)


def format_blocks(blocks):
    """
    Converts a list of block objects into JSON.

    Args:
        blocks: A list of block objects.

    Returns: A JSON list of block objects.

    """
    blocks_formatted = dict()
    for block in blocks:
        blocks_formatted[block] = blocks[block].get_description()
    return blocks_formatted


def get_block_visibility(config):
    """
    Creates and returns a dictionary containing for looking up the visibility of a given block.

    Args:
        config: The configuration where block information is read.

    Returns: A dictionary with block-visibility as key-value pairs.

    """
    vis = dict()
    for block in config["blocks"]:
        vis[block["name"]] = block["visible"]
    return vis

