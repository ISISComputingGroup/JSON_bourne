from lxml import html
import requests
import json
from block import Block
import logging

# defines a function and stores value as 'title'
def shorten_title(title):
    """
    Gets a PV title by shortening its address to the last segment.

    Args:
        title: The PV address as string.

    Returns: The last segment of the input PV address as string.

    """
    # recieve the new value as a string for the RC value
    # split string of the value at each colon
    # look at each seperate string
    # if there is a match on the block name
    # new condition, if there is a match 'RC'
    # new condition, if there is a value
    # store it as the title
    # else, move to the next block of code


    # new variable declared as 'number'
    # finding the last ':' in the 'title'
    number = title.rfind(':')
    # returns the title where ':' is found
    return title[number + 1:]

def shorten_rc_title(title):
    """
    Gets a PV title by shortening its address to the last segment.

    Args:
        title: The PV address as string.

    Returns: The last segment of the input PV address as string.

    """
    # recieve the new value as a string for the RC value
    # split string of the value at each colon
    # look at each seperate string
    # if there is a match on the block name
    # new condition, if there is a match 'RC'
    # new condition, if there is a value
    # store it as the title
    # else, move to the next block of code


    # new variable declared as 'number'
    # finding the last ':' in the 'title'

    title = title.split(':')
    rc_name = "RC"
    value_name = ["HIGH.VAL", "LOW.VAL", "INRANGE.VAL", "ENABLED.VAL"]
    title_list = []

    if rc_name in title:
        title_list.append(title[-3])
        title_list.append(rc_name)
        for name in value_name:
            if name in title:
                title_list.append(name)
                title = ':'.join(title_list)
                return title
    else:
        title = title[-1]
        return title


def get_rc_values_for_block(block_name, pvs):
    """Search pvs for RC values for given block and return them"""
    for k, v in pvs.items():
        block_names = k.split(':')
        if block_name == block_names[0]:
		return v

def get_rc_values_for_block_from_object(block_name, pvs):
    """Search pvs for RC values for given block and return them"""
    items = pvs.items()
    def key_matches(key):
    	return key.split(':')[0] == block_name
    return [value.get_value() for key, value in items if key_matches(key)]


def set_rc_values_for_block_from_pvs(block_object, pvs):
    """Search pvs for RC values for given block and return them"""
    block_name = block_object.get_name()
    items = pvs.items()

    for k, v in items:
        test_block_name = k.split(':')[0]
        if block_name == test_block_name:
            if "LOW.VAL" == k.split(':')[-1]:
                low_rc = block_object.set_rc_low(v.get_value())
            if "HIGH.VAL" == k.split(':')[-1]:
                high_rc = block_object.set_rc_high(v.get_value())
            if "INRANGE.VAL" == k.split(':')[-1]:
                inrange_rc = block_object.set_rc_inrange(v.get_value())
                return low_rc, high_rc, inrange_rc

def set_rc_values_for_blocks(block_objects, pvs):
    """Set all RC values for all the given blocks"""
    for object in block_objects:
        set_rc_values_for_block_from_pvs(object,pvs)

def add_rc_values(pvs, blocks):
    """Look for RC values in the supplied list o pvs and assign them to the correct block."""


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

    assert(len(titles) == len(status_text))
    assert(len(titles) == len(info))

    for i in range(len(titles)):
        try:
            block_raw = info[i].text
            if block_raw == "null":
                    value = "null"
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
            logging.error("Unable to decode " + str(titles[i]))

    return blocks

# ans = get_info("http://localhost:4812/group?name=INST")
# for a in ans:
#     print a


