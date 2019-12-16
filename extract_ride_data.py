#!/usr/bin/env python3

import os
from datetime import datetime
import re
import json


class LogHeader():
    def __init__(self, log_input_file):
        self.log_title = log_input_file.readline()
        log_input_file.readline()
        self.serial_no = log_input_file.readline()
        self.vin = log_input_file.readline()
        self.firmware_rev = log_input_file.readline()
        self.board_rev = log_input_file.readline()
        self.model = log_input_file.readline()
        log_input_file.readline()
        self.log_entries_count = log_input_file.readline()
        log_input_file.readline()
        self.column_headings = log_input_file.readline()
        self.column_divider = log_input_file.readline()


class LogEntry():
    entry: int
    event: str
    event_type: str
    conditions: str

    def __init__(self, log_text):
        try:
            self.entry = int(log_text[:9].strip())
            timestamp_text = log_text[10:32].strip()
            if timestamp_text:
                try:
                    self.timestamp = datetime.strptime(timestamp_text, '%m/%d/%Y %H:%M:%S')
                except ValueError:
                    self.timestamp = None
            message = log_text[33:].strip()
            [self.event_type, self.event] = self.type_and_event_from_message(message)
            if self.has_conditions():
                self.event = log_text[33:59].strip()
                self.conditions = log_text[60:].strip()
            else:
                self.conditions = None
        except Exception as e:
            print(log_text)
            raise e

    @classmethod
    def type_and_event_from_message(cls, message: str) -> [str]:
        event_type = ''
        event_contents = message
        if message.startswith('0x'):
            event_type = 'BINARY'
        elif re.match('^[A-Z][a-z]+ing', message):
            event_type = message.split(' ')[0].upper()
            event_contents = ''
        elif message.endswith(' Connected'):
            event_type = 'CONNECTED'
        elif message.endswith(' Disconnected'):
            event_type = 'DISCONNECTED'
        elif message.startswith('INFO:'):
            event_type = 'INFO'
            event_contents = message[6:]
        elif message.startswith('DEBUG:'):
            event_type = 'DEBUG'
            event_contents = message[7:]
        elif message.startswith('WARNING:'):
            event_type = 'WARNING'
            event_contents = message[8:]
        elif message.endswith(' On') or ' On ' in message:
            event_type = 'ON'
            event_contents = message[:-3]
        elif message.endswith(' Off') or ' Off ' in message:
            event_type = 'OFF'
            event_contents = message[:-4]
        return [event_type, event_contents]

    @classmethod
    def conditions_to_dict(cls, conditions: str) -> dict:
        result = {}
        if ',' in conditions:
            for condition_element in conditions.split(r",\s*"):
                [key, value] = re.split(r"\s*:\s*", condition_element)
                result[key] = value
        else:
            key_positions = re.findall(r"[A-Za-z]+:\s*", conditions)
            for i,j in zip(key_positions[0::2], key_positions[1::2]):
                result[i.group(0).trim()] = conditions[i.end(0):j.start(0)]
        return result

    @property
    def component(self):
        if self.event.startswith('Module '):
            return 'BMS'
        elif 'Sevcon' in self.event:
            return 'Controller'
        elif 'Calex' in self.event:
            return 'Charger'
        return 'MBB'

    def is_notice(self):
        return self.event_type in ['INFO', 'DEBUG', 'WARNING']

    def has_conditions(self):
        return (not self.is_notice() and
                self.event_type not in ['BINARY', 'CONNECTED', 'DISCONNECTED'])

    def conditions_dict(self):
        if self.conditions:
            return self.conditions_to_dict(self.conditions)
        return None

    def is_ride_entry(self):
        return self.entry == 'Riding'

    def ride_conditions(self):
        if self.is_ride_entry():
            return self.conditions_dict()
        else:
            return None

    def is_charge_entry(self):
        return self.entry == 'Charging'

    def to_csv(self, sep=','):
        return sep.join([
            str(self.entry),
            self.timestamp and str(self.timestamp) or '',
            self.component,
            self.event_type,
            self.event,
            self.conditions and self.conditions or ''])

    def to_tsv(self):
        return self.to_csv(sep='\t')

    def to_json(self):
        return json.dumps({
            'entry': self.entry,
            'timestamp': self.timestamp and str(self.timestamp) or '',
            'component': self.component,
            'event_type': self.event_type,
            'event': self.event,
            'conditions': self.conditions
        })


tabular_headers = ['Entry', 'Timestamp', 'Component', 'Type', 'Event', 'Conditions']

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", default='tsv',
                        help="the output format desired: csv,tsv,json")
    parser.add_argument("logfile",
                        help="the parsed log file to process")
    parser.add_argument("--outfile",
                        help="the name of output file to emit")

    args = parser.parse_args()
    log_filepath = args.logfile
    if not os.path.exists(log_filepath):
        print("Log file does not exist: ", log_filepath)
        exit(1)
    output_format = args.format
    line_sep = os.linesep
    output_filepath = args.outfile
    if not output_filepath:
        output_filepath = log_filepath + '.' + output_format

    with open(log_filepath) as log_file:
        # Read header:
        header_info = LogHeader(log_file)
        with open(output_filepath, 'w') as output:
            # Read log entries:
            line = log_file.readline()
            # Write header:
            if output_format == 'csv':
                output.write(','.join(tabular_headers) + line_sep)
            elif output_format == 'tsv':
                output.write('\t'.join(tabular_headers) + line_sep)
            # Process log entries:
            while line:
                log_entry = LogEntry(line)
                if output_format == "csv":
                    output.write(log_entry.to_csv() + line_sep)
                elif output_format == "tsv":
                    output.write(log_entry.to_tsv() + line_sep)
                elif output_format == "json":
                    output.write(log_entry.to_json() + ',' + line_sep)
                line = log_file.readline()
