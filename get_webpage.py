from lxml import html
import requests
import json
from block import Block
import logging
from datetime import datetime


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

    return {shorten_title(titles[i]):
                Block.from_raw(titles[i], status_text[i], info[i].text) for i in range(len(titles))}


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
    except Exception as e:
        logging.error("Output construction failed " + str(e))
        raise e

    return output


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

