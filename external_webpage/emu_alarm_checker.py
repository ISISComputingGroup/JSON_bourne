import logging
import os
from logging.handlers import TimedRotatingFileHandler

class EmuAlarmLogger():

    def __init__(self) -> None:
        self.logger = logging.getLogger("emu_alarm_logger")
        log_filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'log', 'emu_alarm.log')
        handler = TimedRotatingFileHandler(log_filepath, when='midnight', backupCount=30)
        handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
    
    def check_for_alarm(self, blocks):
        self.logger.debug(str(blocks))
