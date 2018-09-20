import re
from collections import OrderedDict
import time


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


def get_instrument_time_since_epoch(instrument_data):
    """
    Return the instrument time as seconds sind epoch.
    """

    inst_time_str = instrument_data['inst_pvs']['TIME_OF_DAY']['value']
    inst_time_struct = time.strptime(inst_time_str, '%m/%d/%Y %H:%M:%S')
    inst_time = time.mktime(inst_time_struct)

    return inst_time


def check_outdated(instrument_data, time_shift_threshold):
    """
    Update the instrument data with the time shift to the webserver.
    :param instrument_data: The data dictionary of an instrument
    :param time_shift_threshold: If the time shift is greater than this value the data is considered outdated
    """
    try:
        inst_time = get_instrument_time_since_epoch(instrument_data)
        current_time = time.time()
        time_diff = abs(current_time - inst_time)
    except:
        time_diff = None

    instrument_data['time_diff'] = time_diff

    if time_diff is not None and time_diff > time_shift_threshold:
        instrument_data['outdated'] = True
    else:
        instrument_data['outdated'] = False


def get_detailed_state_of_specific_instrument(instrument, data, time_shift_threshold):
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
    check_outdated(data[instrument], time_shift_threshold)

    return data[instrument]
