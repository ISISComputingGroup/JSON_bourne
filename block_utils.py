from __future__ import unicode_literals


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


def set_rc_values_for_blocks(blocks):
    """
    Set all RC values for all the given blocks. Blocks contains the blocks and their run control settings
    Args:
        blocks: blocks and run control settings
    """
    for block in blocks.values():
        block_name = block.get_name()

        for k, v in blocks.items():
            if k is None:
                # not a valid key, skip this entry
                continue

            key_parts = k.split(':')
            name = key_parts[0].strip()
            suffix = key_parts[-1]

            if block_name != name:
                # block name does not match, skip this entry
                continue

            if "LOW.VAL" == suffix:
                block.set_rc_low(v.get_value())
            elif "HIGH.VAL" == suffix:
                block.set_rc_high(v.get_value())
            elif "INRANGE.VAL" == suffix:
                block.set_rc_inrange(v.get_value())
            elif "ENABLE.VAL" == suffix:
                block.set_rc_enabled(v.get_value())


def format_blocks(blocks):
    """
    Converts a list of block objects into JSON.

    Args:
        blocks: A dictionary of block names to block objects.

    Returns: A JSON dictionary of block names to block descriptions.

    """
    blocks_formatted = {}
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
