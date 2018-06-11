import json
import re


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


def get_whether_ibex_is_running_on_all_instruments(data, instrument_list_retrieval_errors):
    """
    Gets whether ibex is running for each instrument.
    :param data: The data scraped from the archiver webpage
    :return: A json dictionary containing the states of each instrument (True if running, False otherwise)
    """

    inst_data = {}
    for inst, v in data.items():

        try:
            run_state = v["inst_pvs"]["RUNSTATE"]["value"]
        except (KeyError, TypeError):
            run_state = "UNKNOWN"

        inst_data[inst] = {"is_up": (v != ''),
                           "run_state": run_state}
    active = {
        "error": instrument_list_retrieval_errors,
        "instruments": inst_data}

    return str(json.dumps(active))


def get_detailed_state_of_specific_instrument(instrument, data):
    """
    Gets the detailed state of a specific instrument, used to display the instrument's dataweb screen
    :param instrument: The instrument to get data for
    :param data: The data scraped from the archiver webpage
    :return: The data from the archiver webpage filtered to only contain data about the requested instrument
    """
    if instrument not in data.keys():
        raise ValueError(str(instrument) + " not known")
    if data[instrument] == "":
        raise ValueError("Instrument has become unavailable")
    try:
        return str(json.dumps(data[instrument]))
    except Exception as err:
        raise ValueError("Unable to convert instrument data to JSON: %s" % err.message)
