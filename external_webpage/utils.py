import zlib


def dehex_and_decompress(value):
    """
    Decompress and dehex pv value
    Args:
        value: value to translate

    Returns: dehexed value

    """
    try:
        # If it comes as bytes then cast to string
        value = value.decode("utf-8")
    except AttributeError:
        pass

    return zlib.decompress(bytes.fromhex(value)).decode("utf-8")
