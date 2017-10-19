from lxml import html
import requests
import json
from block import Block
from block_utils import (format_blocks, set_rc_values_for_block_from_pvs,
        set_rc_values_for_blocks, shorten_title)
import logging

logger = logging.getLogger('JSON_bourne')

PORT_INSTPV = 4812
PORT_BLOCKS = 4813
PORT_CONFIG = 8008

def ascii_to_string(ascii):
    """
    Converts a list of ascii characters into a string.

    Args:
        ascii: A list of ascii characters.

    Returns: The input as string.

    """
    string = ''
    for char in ascii:
        # Filters out non-numeric ascii codes (e.g. with a "," at the end)
        char = filter(lambda x: x in '0123456789', char)

        # If char is empty after filtering
        if len(char) == 0:
            continue

        # Convert char to int
        char = int(char)

        # Avoids printing nulls
        if char > 0:
            string += chr(char)

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
        logger.error("URL not found: " + str(url))
        raise e

    blocks = {}

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

    assert(len(titles) == len(status_text))
    assert(len(titles) == len(info))

    for i in range(len(titles)):
        try:
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
                if len(block_split) < 4:
                    # Missing a value
                    continue
                else:
                    value = block_split[value_index]
                    alarm = block_split[alarm_index]

            name = shorten_title(titles[i])
            status = status_text[i]
            blocks[name] = Block(name, status, value, alarm, True)
        except Exception as e:
            logger.error("Unable to decode " + str(titles[i]))

    return blocks


def get_instpvs(url, blocks_all):
    """
    Extracts and formats a list of relevant instrument PVs from all instrument PVs.

    Args:
        url: The source of the instrument PV information.

    Returns: A trimmed list of instrument PVs.

    """
    wanted = {}
    rc = {}
    ans = get_info(url)

    required_pvs = ["RUNSTATE", "RUNNUMBER", "_RBNUMBER", "TITLE", "DISPLAY", "_USERNAME", "STARTTIME",
                    "RUNDURATION", "RUNDURATION_PD", "GOODFRAMES", "GOODFRAMES_PD", "RAWFRAMES", "RAWFRAMES_PD",
                    "PERIOD", "NUMPERIODS", "PERIODSEQ", "BEAMCURRENT", "TOTALUAMPS", "COUNTRATE", "DAEMEMORYUSED",
                    "TOTALCOUNTS", "DAETIMINGSOURCE", "MONITORCOUNTS", "MONITORSPECTRUM", "MONITORFROM", "MONITORTO",
                    "NUMTIMECHANNELS", "NUMSPECTRA"]

    try:
        set_rc_values_for_blocks(blocks_all.values(), ans)
    except Exception as e:
        logging.error("Error in setting rc values for blocks: " + str(e))

    for pv in required_pvs:
        if pv + ".VAL" in ans:
            wanted[pv] = ans[pv + ".VAL"]

    try:
        convert_seconds(wanted["RUNDURATION"])
    except KeyError:
        pass

    try:
        convert_seconds(wanted["RUNDURATION_PD"])
    except KeyError:
        pass

    return wanted


def convert_seconds(block):
    """
    Receives the value from the block and converts to hours, minutes and seconds.

    Args:
        block: the block to convert

    """
    if not block.is_connected():
        return
    old_value = block.get_value()
    seconds = int(old_value) % 60
    minutes = int(old_value) / 60
    hours = minutes / 60
    minutes %= 60

    if hours == 0 and minutes == 0:
        block.set_value(old_value + " s")
    elif hours == 0:
        block.set_value(str(minutes) + " min " + str(seconds) + " s")
    else:
        block.set_value(str(hours) + " hr " + str(minutes) + " min " + str(seconds) + " s")


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
        logger.error("JSON conversion failed: " + str(e))
        logger.error("JSON was: " + str(config))
        raise e

    try:
        block_vis = get_block_visibility(config)

        # read blocks
        blocks_log = get_info('http://%s:%s/group?name=BLOCKS' % (host, PORT_BLOCKS))
        blocks_nolog = get_info('http://%s:%s/group?name=DATAWEB' % (host, PORT_BLOCKS))
        blocks_all = dict(blocks_log.items() + blocks_nolog.items())

        # get block visibility from config
        for block in blocks_all:
            blocks_all[block].set_visibility(block_vis.get(block))
    except Exception as e:
        logger.error("Failed to read blocks: " + str(e))

    inst_pvs = format_blocks(get_instpvs('http://%s:%s/group?name=INST' % (host, PORT_INSTPV), blocks_all))

    groups = {}
    for group in config["groups"]:
        blocks_all_formatted = format_blocks(blocks_all)
        blocks = {}
        for block in group["blocks"]:
            if block in blocks_all_formatted.keys():
                blocks[block] = blocks_all_formatted[block]
        groups[group["name"]] = blocks

    try:
        output = {}
        output["config_name"] = config["name"]
        output["groups"] = groups
        output["inst_pvs"] = inst_pvs
    except Exception as e:
        logger.error("Output construction failed " + str(e))
        raise e

    return output

def get_block_visibility(config):
    """
    Creates and returns a dictionary containing for looking up the visibility of a given block.

    Args:
        config: The configuration where block information is read.

    Returns: A dictionary with block-visibility as key-value pairs.

    """
    vis = {}
    for block in config["blocks"]:
        vis[block["name"]] = block["visible"]
    return vis

