from builtins import object


class ArchiveMother(object):
    """
    Data mother for JSON objects.
    """

    index = 0

    @staticmethod
    def create_info_page(channels):
        return {"Channels": channels, "Enabled": True}

    @staticmethod
    def create_channel(name=None, is_connected=True, value="0.000", alarm="", units=""):
        """
        Create a channel
        :param name: name of the channel
        :param is_connected: True if connected; False otherwise
        :param value: value from the channel
        :param alarm: alarm for the channel
        :param units: units of the current value
        :return: channel
        """
        if name is None:
            ArchiveMother.index += 1
            name = "BLOCK_{index}".format(index=ArchiveMother.index)

        if is_connected:
            current_value = {
                "Alarm": alarm,
                "Timestamp": "2017-10-19 09:04:16.141466495",
                "Units": units,
                "Value": value,
            }
        else:
            current_value = {"Value": "null"}

        return {
            "Capacity": 2,
            "Channel": "TE:NDW1798:CS:SB:{channel_name}".format(channel_name=name),
            "Connected": is_connected,
            "Current Value": current_value,
            "Internal State": "Connected",
            "Last Archived Value": {
                "Alarm": "",
                "Timestamp": "2017-10-19 15:50:58.305000000",
                "Units": "uA hour",
                "Value": "0.000",
            },
            "Mechanism": "30.00 sec scan, max. 60 repeats",
            "Overruns": 0,
            "Queue Avg.": 1.2678049824964753e-13,
            "Queue Len.": 0,
            "Queue Max.": 1,
            "Received Values": 1,
            "State": True,
        }


class ConfigMother(object):
    @staticmethod
    def create_config(name="conf", blocks=None, groups=None):
        if blocks is not None:
            final_blocks = blocks
        else:
            final_blocks = []

        if groups is not None:
            final_groups = groups
        else:
            final_groups = []

        return {
            "blocks": final_blocks,
            "groups": final_groups,
            "iocs": [
                {
                    "macros": [],
                    "pvs": [],
                    "name": "SIMPLE",
                    "autostart": False,
                    "pvsets": [],
                    "component": None,
                    "restart": False,
                    "simlevel": "devsim",
                }
            ],
            "description": "vmvm",
            "component_iocs": [
                {
                    "macros": [],
                    "pvs": [],
                    "name": "SIMPLE",
                    "autostart": False,
                    "pvsets": [],
                    "component": None,
                    "restart": False,
                    "simlevel": "devsim",
                },
                {
                    "macros": [],
                    "pvs": [],
                    "name": "SIMPLE",
                    "autostart": True,
                    "pvsets": [],
                    "component": "simple",
                    "restart": False,
                    "simlevel": "none",
                },
                {
                    "macros": [],
                    "pvs": [],
                    "name": "INSTETC_01",
                    "autostart": True,
                    "pvsets": [],
                    "component": "_base",
                    "restart": True,
                    "simlevel": "none",
                },
                {
                    "macros": [],
                    "pvs": [],
                    "name": "ISISDAE_01",
                    "autostart": True,
                    "pvsets": [],
                    "component": "_base",
                    "restart": True,
                    "simlevel": "none",
                },
                {
                    "macros": [],
                    "pvs": [],
                    "name": "ALARM",
                    "autostart": True,
                    "pvsets": [],
                    "component": "_base",
                    "restart": True,
                    "simlevel": "none",
                },
                {
                    "macros": [],
                    "pvs": [],
                    "name": "ARACCESS",
                    "autostart": True,
                    "pvsets": [],
                    "component": "_base",
                    "restart": True,
                    "simlevel": "none",
                },
            ],
            "components": [{"name": "simple"}],
            "history": [
                "2016-11-30 11:59:41",
                "2016-12-08 09:50:24",
                "2017-03-14 11:08:25",
                "2017-05-04 17:01:57",
                "2017-10-03 15:03:54",
                "2017-10-03 15:12:13",
            ],
            "synoptic": "-- NONE --",
            "name": name,
        }

    @staticmethod
    def create_block(block_name, is_visibile=True):
        return {
            "log_rate": 30.0,
            "log_deadband": 0.0,
            "component": None,
            "runcontrol": False,
            "Precision": 3,
            "visible": is_visibile,
            "pv": "TE:NDW1798:SIMPLE:VALUE1",
            "name": block_name,
            "highlimit": 0.0,
            "log_periodic": True,
            "lowlimit": 0.0,
            "local": True,
        }

    @staticmethod
    def create_group(group_name, blocks):
        return {"component": None, "blocks": blocks, "name": group_name}
