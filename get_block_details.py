from lxml import html
import requests
import json
from block import Block
import logging

def shorten_title(title):
    """
    Gets a PV title by shortening its address to the last segment.

    If the title contains an RC value the PV title & the RC value
    are returned.

    Args:
        title: The PV address as string.

    Returns: The last segment of the input PV address as string.

    """
    title_parts = title.split(':')
    rc_values = ["HIGH.VAL", "LOW.VAL", "INRANGE.VAL", "ENABLED.VAL"]

    if "RC" in title_parts and title_parts[-1] in rc_values:
        return ':'.join(title_parts[-3:])
    else:
        return title_parts[-1]


def set_rc_values_for_block_from_pvs(block, pvs):
    """Search pvs for RC values for given block and return them"""
    block_name = block.get_name()
    items = pvs.items()

    for k, v in items:
        if k is None:
            # not a valid key, skip this entry
            continue

        key_parts = k.split(':')
        name = key_parts[0]
        suffix = key_parts[-1]

        if block_name != name:
            # block name does not match, skip this entry
            continue

        if "LOW.VAL" == suffix:
            block.set_rc_low(v.get_value())
        if "HIGH.VAL" == suffix:
            block.set_rc_high(v.get_value())
        if "INRANGE.VAL" == suffix:
            block.set_rc_inrange(v.get_value())

def set_rc_values_for_blocks(blocks, pvs):
    """Set all RC values for all the given blocks"""
    for block in blocks:
        set_rc_values_for_block_from_pvs(block, pvs)

