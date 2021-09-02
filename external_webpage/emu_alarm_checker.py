import logging
import os
from logging.handlers import TimedRotatingFileHandler
import time


class EmuAlarmLogger(object):

    def __init__(self, host) -> None:
        self.host = host
        if self.host_is_correct():
            self.logger = logging.getLogger("emu_alarm_logger")
            log_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", 'log', 'emu_alarm.log')
            handler = TimedRotatingFileHandler(log_filepath, when='midnight', backupCount=30)
            handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(handler)
            self.logger.error("Started emu alarm logger")
            self.last_alarm_check = time.strftime('%Y-%m-%d %H:%M')

    def check_for_alarm(self, blocks):
        if self.host_is_correct():
            self.logger.error(f"Alarms checked at {time.strftime('%Y-%m-%d %H:%M')}")
            for block in blocks.values():
                if block.alarm != "":
                    self.logger.error(f"{block.name}: {block.alarm}")
    
    def host_is_correct(self):
        return self.host.lower() == "ndxemu"
