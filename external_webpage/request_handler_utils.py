from builtins import str
import re
from collections import OrderedDict
import time
import logging

logger = logging.getLogger('JSON_bourne')


def get_instrument_and_callback(path):
    """
    Looks at the path used to connect and picks out the callback function and the instrument name.
    Args:
        path (str): the requested path

    Returns:
        tuple: (instrument name, callback mathod name)

    """
    # JSONP requires a response of the format "name_of_callback(json_string)"
    # e.g. myFunction({ "a": 1, "b": 2})
    callback = re.findall('/?callback=(\w+)&', path)

    # Look for the instrument data
    instruments = re.findall('&Instrument=([^&]+)&', path)

    if len(callback) != 1:
        raise ValueError("Invalid number of callbacks specified: {}".format(path))

    if len(instruments) != 1:
        raise ValueError("Invalid number of instruments specified: {}".format(path))

    return instruments[0].upper(), callback[0]


def get_summary_details_of_all_instruments(data):
    """
    Gets whether ibex is running for each instrument.
    :param data: The data scraped from the archiver webpage
    :return: A json dictionary containing the states of each instrument (True if running, False otherwise)
    """

    inst_data = OrderedDict()
    ordered_inst_list = sorted(data.keys(), key=lambda s: s.lower())
    for inst in ordered_inst_list:
        v = data[inst]

        try:
            run_state = v["inst_pvs"]["RUNSTATE"]["value"]
        except (KeyError, TypeError):
            run_state = "UNKNOWN"

        inst_data[inst] = {"is_up": (v != ''),
                           "run_state": run_state}

    return inst_data


def get_instrument_time_since_epoch(instrument_name, instrument_data):
    """
    Return the instrument time as seconds since epoch.

    :param instrument_name: The name of the instrument
    :param instrument_data: The data associated with the instrument
    :return: the instrument time as seconds since epoch.

    :raises: KeyError: instrument time cannot be parsed from instrument_data
    :raises: ValueError: if instrument time has wrong time format
    """

    try:
        channel = instrument_data['Channel']
    except KeyError:
        channel = "UNKNOWN"

    time_format = '%m/%d/%Y %H:%M:%S'
    try:
        tod = 'TIME_OF_DAY'
        inst_time_str = instrument_data['inst_pvs'][tod]['value']
    except KeyError:
        logger.exception(f"{instrument_name}: Cannot find {tod} in PV {channel}.")
        raise

    try:
        inst_time_struct = time.strptime(inst_time_str, time_format)
    except ValueError:
        logger.exception(f"{instrument_name}: Value {inst_time_str} from PV {channel} does not match time format "
                         f"{time_format}.")
        raise

    try:
        inst_time = time.mktime(inst_time_struct)
    except (ValueError, OverflowError):
        inst_time = None
        logger.error(f"{instrument_name}: Cannot parse value {inst_time} from PV {channel} as time")

    return inst_time


def set_time_shift(instrument_name, instrument_data, time_shift_threshold,
                   extract_time_from_instrument_func=get_instrument_time_since_epoch,
                   current_time_func=time.time):
    """
    Update the instrument data with the time shift to the webserver.

    :param instrument_name: The name of the instrument
    :param instrument_data: The data dictionary of the instrument
    :param time_shift_threshold: If the time shift is greater than this value the data is considered outdated
    """
    try:
        inst_time = extract_time_from_instrument_func(instrument_name, instrument_data)
        current_time = current_time_func()
        time_diff = int(round(abs(current_time - inst_time)))
    except (ValueError, TypeError, KeyError):
        time_diff = None

    try:
        instrument_data['time_diff'] = time_diff

        if time_diff is not None and time_diff > time_shift_threshold:
            instrument_data['out_of_sync'] = True
            logger.warning(f"There is a time shift of {time_diff} seconds between {instrument_name} and web server")
        else:
            instrument_data['out_of_sync'] = False
    except TypeError:
        logger.error(f"Cannot set time shift information for {instrument_name}.")


def get_detailed_state_of_specific_instrument(instrument, data, time_shift_threshold=5*60):
    """
    Gets the detailed state of a specific instrument, used to display the instrument's dataweb screen
    :param instrument: The instrument to get data for
    :param data: The data scraped from the archiver webpage
    :param time_shift_threshold: The allowed time difference in seconds between the instrument and the webserver time
    :return: The data from the archiver webpage filtered to only contain data about the requested instrument
    """
    if instrument not in data.keys():
        raise ValueError(str(instrument) + " not known")
    if data[instrument] == "":
        raise ValueError("Instrument has become unavailable")
    set_time_shift(instrument, data[instrument], time_shift_threshold)

    return data[instrument]
