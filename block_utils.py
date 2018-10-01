from __future__ import unicode_literals
import logging

from collections import OrderedDict

logger = logging.getLogger('JSON_bourne')

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
    rc_values = ["HIGH.VAL", "LOW.VAL", "INRANGE.VAL", "ENABLE.VAL"]

    if "RC" in title_parts and title_parts[-1] in rc_values:
        return ':'.join(title_parts[-3:])
    else:
        return title_parts[-1]


def set_rc_values_for_blocks(blocks, run_control_pvs):
    """
    Set all RC values for all the given blocks. Blocks contains the blocks and their run control settings
    Args:
        blocks: dictionary of {pv_names : block_objects} containing info blocks
        run_control_pvs: dictionary of {pv_names : block_objects} containing run control settings
    """
    for pv, block_object in run_control_pvs.items():
        pv_parts = pv.split(':')
        name = pv_parts[0].strip()
        suffix = pv_parts[-1]

        try:
            block = blocks[name]

            if "LOW.VAL" == suffix:
                block.set_rc_low(block_object.get_value())
            elif "HIGH.VAL" == suffix:
                block.set_rc_high(block_object.get_value())
            elif "INRANGE.VAL" == suffix:
                block.set_rc_inrange(block_object.get_value())
            elif "ENABLE.VAL" == suffix:
                block.set_rc_enabled(block_object.get_value())
        except KeyError as e:
            logging.info("Could not find block but it has runcontrol pvs {}".format(name))


def format_blocks(blocks):
    """
    Converts a list of block objects into JSON.

    Args:
        blocks: A dictionary of block names to block objects.

    Returns: A JSON dictionary of block names to block descriptions.

    """
    blocks_formatted = OrderedDict()
    for name, block in blocks.items():
        blocks_formatted[name] = block.get_description()

    return blocks_formatted


def format_block_value(val, precision):
    """
    Formats block values using the same rules as the blocks screen in the GUI.
    Args:
        val (str): the block value to format
        precision (int): the precision to format the block to. If None then will not format.
    Returns:
        the formatted block value
    """

    small_number_threshold = 0.001
    big_number_threshold = 1000000
    assert small_number_threshold < big_number_threshold

    # No precision specified = do not format.
    if precision is None or precision < 0:
        return u"{}".format(val)
    try:
        float_val = float(val)

        if small_number_threshold < abs(float_val) < big_number_threshold or float_val == 0:
            format_str = u"{{:.{}f}}".format(precision)
        else:
            format_str = u"{{:.{}G}}".format(precision)

        return format_str.format(float_val)
    except (ValueError, TypeError):
        # If number does not parse as a float, or formatting failed, just return it in string form.
        return u"{}".format(val)
