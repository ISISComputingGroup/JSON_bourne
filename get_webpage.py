from lxml import html
import requests
import json
from block import Block
import logging


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


def ascii_to_string(ascii):
    """
    Converts a list of ascii characters into a string.

    Args:
        ascii: A list of ascii characters.

    Returns: The input as string.

    """
    string = ''
    for char in ascii:
        if char:
            string += chr(int(char))
    return string


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

    blocks = dict()

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

    for i in range(len(titles)):
        block_raw = info[i].text
        if block_raw == "null":
                value = "null"
                alarm = "null"
        elif "DAE:STARTTIME.VAL" in titles[i]:
            value_index = 1
            alarm_index = 2
            block_split = block_raw.split("\t", 2)
            value = block_split[value_index]
            alarm = block_split[alarm_index]
        elif "DAE:TITLE.VAL" in titles[i] or "DAE:_USERNAME.VAL" in titles[i]:
            # Title and user name are ascii codes spaced by ", "
            value_index = 2
            block_split = block_raw.split(None, 2)
            value_ascii = block_split[value_index].split(", ")
            try:
                value = ascii_to_string(value_ascii)
            except Exception as e:
                # Put this here for the moment, title/username need fixing anyway
                value = "Unknown"
            alarm = "null"
        else:
            value_index = 2
            alarm_index = 3
            block_split = block_raw.split(None, 3)
            value = block_split[value_index]
            alarm = block_split[alarm_index]

        name = shorten_title(titles[i])
        status = status_text[i]
        blocks[name] = Block(status, value, alarm, True)

    return blocks


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
    config = json.loads(corrected_page)
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

    output = dict()
    output["config_name"] = config["name"]
    output["groups"] = groups
    output["inst_pvs"] = format_blocks(get_instpvs('http://%s:%s/group?name=INST' % (host, PORT_INSTPV)))

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

