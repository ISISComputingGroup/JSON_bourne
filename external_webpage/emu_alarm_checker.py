import logging
import os
from logging.handlers import TimedRotatingFileHandler
import time

main_logger = logging.getLogger('JSON_bourne')


class EmuAlarmLogger(object):

    def __init__(self) -> None:
        self.logger = logging.getLogger("emu_alarm_logger")
        log_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", 'log', 'emu_alarm.log')
        handler = TimedRotatingFileHandler(log_filepath, when='midnight', backupCount=30)
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.logger.error("Started emu alarm logger")

    def check_for_alarm(self, blocks):
        self.logger.error(f"Alarms checked at {time.strftime('%Y-%m-%d %H:%M')}")
        for block in blocks.values():
            if block.alarm != "":
                self.logger.error(f"{block.name}: {block.alarm}")
