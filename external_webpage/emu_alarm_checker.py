import logging
import os
from logging.handlers import DEFAULT_SOAP_LOGGING_PORT, TimedRotatingFileHandler
import time
import glob
from typing import List, Dict
import argparse
import pprint


log_name = 'emu_alarm.log'
log_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", 'log')
log_filepath = os.path.join(log_dir, log_name)


class EmuAlarmLogger(object):

    def __init__(self, host) -> None:
        self.host = host
        if self.host_is_correct():
            self.logger = logging.getLogger("emu_alarm_logger")
            handler = TimedRotatingFileHandler(log_filepath, when='midnight', backupCount=30)
            handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(handler)
            self.logger.error("Started emu alarm logger")
            self.last_alarm_check = time.strftime('%Y-%m-%d %H:%M')

    def check_for_alarm(self, blocks):
        if self.host_is_correct():
            self.logger.error(f"Alarms checked at: {time.strftime('%Y-%m-%d %H:%M')}")
            for block in blocks.values():
                if block.alarm != "":
                    self.logger.error(f"[{block.name}: {block.alarm}")
    
    def host_is_correct(self):
        return self.host.lower() == "ndxemu"


class EmuAlarmChecker(object):

    def __init__(self) -> None:
        self.alarm_log_filenames = glob.glob(f"{log_filepath}*")

    def filter_alarms_in_logs(self, blocks_to_ignore=[]) -> Dict[str, List[str]]:
        filtered_logs: Dict[str, List[str]] = {}
        for alarm_log_filename in self.alarm_log_filenames:
            with open(alarm_log_filename, 'r') as alarm_log_file:
                filtered_logs[alarm_log_filename] = self.filter_alarms_in_log(alarm_log_file, blocks_to_ignore)
        return filtered_logs

    def filter_alarms_in_log(self, alarm_log_file, blocks_to_ignore=[]) -> List[str]:
        filtered_log = []
        for line in alarm_log_file:
            line_without_date = line.split("[")[1]
            block_name = line_without_date.split(":")[0]
            if all(ignored_block != block_name for ignored_block in blocks_to_ignore):
                filtered_log.append(line)
        return filtered_log
    
    def print_filtered_alarm_logs(self, blocks_to_ignore=[]) -> None:
        print(self.filter_alarms_in_logs(blocks_to_ignore))

    def reformat_to_use_square_bracket(self):
        for alarm_log_filename in self.alarm_log_filenames:
            reformatted_lines = []
            with open(alarm_log_filename, 'r') as alarm_log_file:
                for line in alarm_log_file:
                    line_split_by_space = line.split(" ")
                    line_split_by_space[2] = "[" + line_split_by_space[2]
                    reformatted_line = " ".join(line_split_by_space)
                    reformatted_lines.append(reformatted_line)
            with open(alarm_log_filename, 'w') as alarm_log_file:
                alarm_log_file.writelines(reformatted_lines)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    # The following are blocks in alarm that we may want to ignore:
    # danfysik_auto_onoff field_hifi field_t20 t20_stable Beamlog_TS1_Freq Beamlog_Raw_Frames_Total Temp_SP Beamlog_Good_Frames_Period Beamlog_Good_Frames_Total Beamlog_Raw_Frames_Period Beamlog_Count_Rate 
    # field_ZF_status field_ZF_x field_ZF_y field_ZF_z field_ZF_magnitude
    default_to_ignore = ["Alarms checked at", "Started emu alarm logger"]
    argparser.add_argument("-b", "--blocks-to-ignore", nargs="+", default=[], dest="blocks_to_ignore")
    argparser.add_argument("-r", "--reformat-to-use-square-bracket", action="store_true", dest="reformat_to_use_square_bracket")
    args = argparser.parse_args()
    emu_alarm_checker = EmuAlarmChecker()
    if args.reformat_to_use_square_bracket:
        emu_alarm_checker.reformat_to_use_square_bracket()
    blocks_to_ignore = default_to_ignore + args.blocks_to_ignore
    if blocks_to_ignore != default_to_ignore:
        emu_alarm_checker.print_filtered_alarm_logs(blocks_to_ignore=blocks_to_ignore)
