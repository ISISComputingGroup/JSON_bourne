class ArchiveMother(object):
    """
    Data mother for JSON objects.
    """
    index = 0

    @staticmethod
    def create_info_page(channels):
        return {u'Channels': channels,
                u'Enabled': True}

    @staticmethod
    def create_channel(name=None, is_connected=True, value=u"0.000", alarm=u"", units=u""):
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
            current_value = {u'Alarm': alarm,
                       u'Timestamp': u'2017-10-19 09:04:16.141466495',
                       u'Units': units,
                       u'Value': value}
        else:
            current_value = {u'Value': "null"}

        return {u'Capacity': 2,
                u'Channel': u'TE:NDW1798:CS:SB:{channel_name}'.format(channel_name=name),
                u'Connected': is_connected,
                u'Current Value': current_value,
                u'Internal State': u'Connected',
                u'Last Archived Value': {u'Alarm': u'',
                                         u'Timestamp': u'2017-10-19 15:50:58.305000000',
                                         u'Units': u'uA hour',
                                         u'Value': u'0.000'},
                u'Mechanism': u'30.00 sec scan, max. 60 repeats',
                u'Overruns': 0,
                u'Queue Avg.': 1.2678049824964753e-13,
                u'Queue Len.': 0,
                u'Queue Max.': 1,
                u'Received Values': 1,
                u'State': True}


class ConfigMother():

    @staticmethod
    def create_config(name="conf"):

        blocks = []
        """[{
                "log_rate": 30.0,
                "log_deadband": 0.0,
                "component": None,
                "runcontrol": False,
                "visible": True,
                "pv": "TE:NDW1798:SIMPLE:VALUE1",
                "name": "NEW_BLOCK_4",
                "highlimit": 0.0,
                "log_periodic": True,
                "lowlimit": 0.0,
                "local": True
            }]"""
        groups = []
        """[{
                "component": None,
                "blocks": ["NEW_BLOCK"],
                "name": "NEW_GROUP"
            }]"""


        return {
            "blocks": blocks,
            "groups": groups,
            "iocs": [{
                "macros": [],
                "pvs": [],
                "name": "SIMPLE",
                "autostart": False,
                "pvsets": [],
                "component": None,
                "restart": False,
                "simlevel": "devsim"
            }],
            "description": "vmvm",
            "component_iocs": [{
                "macros": [],
                "pvs": [],
                "name": "SIMPLE",
                "autostart": False,
                "pvsets": [],
                "component": None,
                "restart": False,
                "simlevel": "devsim"
            }, {
                "macros": [],
                "pvs": [],
                "name": "SIMPLE",
                "autostart": True,
                "pvsets": [],
                "component": "simple",
                "restart": False,
                "simlevel": "none"
            }, {
                "macros": [],
                "pvs": [],
                "name": "INSTETC_01",
                "autostart": True,
                "pvsets": [],
                "component": "_base",
                "restart": True,
                "simlevel": "none"
            }, {
                "macros": [],
                "pvs": [],
                "name": "ISISDAE_01",
                "autostart": True,
                "pvsets": [],
                "component": "_base",
                "restart": True,
                "simlevel": "none"
            }, {
                "macros": [],
                "pvs": [],
                "name": "ALARM",
                "autostart": True,
                "pvsets": [],
                "component": "_base",
                "restart": True,
                "simlevel": "none"
            }, {
                "macros": [],
                "pvs": [],
                "name": "ARACCESS",
                "autostart": True,
                "pvsets": [],
                "component": "_base",
                "restart": True,
                "simlevel": "none"
            }],
            "components": [{
                "name": "simple"
            }],
            "history": ["2016-11-30 11:59:41", "2016-12-08 09:50:24", "2017-03-14 11:08:25", "2017-05-04 17:01:57",
                        "2017-10-03 15:03:54", "2017-10-03 15:12:13"],
            "synoptic": "-- NONE --",
            "name": name,
            }
