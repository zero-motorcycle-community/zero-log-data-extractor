#!/usr/bin/env python3

import os
from datetime import datetime
import re
import json
from typing import List


class LogHeader:
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


class LogEntry:
    entry: int
    event: str
    event_level: str
    event_type: str
    component: str
    conditions: dict

    def __init__(self, log_text):
        try:
            self.entry = int(log_text[:9].strip())
            timestamp_text = log_text[10:32].strip()
            if timestamp_text:
                try:
                    self.timestamp = datetime.strptime(timestamp_text, '%m/%d/%Y %H:%M:%S')
                except ValueError:
                    self.timestamp = ''
            message = log_text[33:].strip()
            for k, v in self.decode_message(message).items():
                setattr(self, k, v)
        except Exception as e:
            print(log_text)
            raise e

    @classmethod
    def decode_message(cls, message: str) -> dict:
        event_type = ''
        event_contents = message
        event_level = ''
        component = 'MBB'
        conditions = {}

        # Extract and strip log level:
        if event_contents.startswith('INFO:'):
            event_level = 'INFO'
            event_contents = event_contents[6:].strip()
        elif event_contents.startswith('DEBUG:'):
            event_level = 'DEBUG'
            event_contents = event_contents[7:].strip()
        elif event_contents.startswith('- DEBUG:'):
            event_level = 'DEBUG'
            event_contents = event_contents[9:].strip()
        elif event_contents.startswith('WARNING:'):
            event_level = 'WARNING'
            event_contents = event_contents[8:].strip()
        elif event_contents.startswith('ERROR:'):
            event_level = 'ERROR'
            event_contents = event_contents[7:].strip()

        # Check contents for event type:
        if event_contents.startswith('0x'):
            event_type = 'UNKNOWN'
            event_contents = ''
        elif event_contents.startswith('Riding'):
            event_type = 'RIDING'
        elif event_contents.startswith('Charging'):
            event_type = 'CHARGING'
        elif event_contents.endswith(' Connected') or event_contents.endswith('Link Up'):
            event_type = 'CONNECTED'
        elif event_contents.endswith(' Disconnected') or event_contents.endswith('Link Down'):
            event_type = 'DISCONNECTED'
        elif event_contents.endswith(' On') or ' On ' in event_contents:
            event_type = 'ON'
        elif event_contents.endswith(' Off') or ' Off ' in event_contents:
            event_type = 'OFF'
        elif 'Limit' in event_contents:
            event_type = 'LIMIT'

        # Check contents for components:
        if event_contents.startswith('Module '):
            component = 'Battery'
        elif 'Sevcon' in event_contents:
            component = 'Controller'
        elif 'Calex' in event_contents:
            component = 'Charger'
        elif 'External Chg' in event_contents:
            component = 'External Charger'

        first_keyword_match = re.search(r"[A-Za-z]+:", event_contents)
        if first_keyword_match:
            idx = first_keyword_match.start(0)
            conditions_field = event_contents[idx:].strip()
            event_contents = event_contents[:idx].strip()
            conditions = cls.conditions_to_dict(conditions_field)

        return {'event_type': event_type,
                'event_level': event_level,
                'component': component,
                'event': event_contents,
                'conditions': conditions}

    @classmethod
    def conditions_to_dict(cls, conditions: str) -> dict:
        result = {}
        key_positions = [match for match in
                         re.finditer(r",?\s*([A-Za-z]+\s*[A-Za-z]+):\s*", conditions)]
        for i, j in zip(key_positions[0::2], key_positions[1::2]):
            key = i.group(1)
            value = conditions[i.end(0):j.start(0)]
            if ',' in value:
                values = re.split(r",\s*", value)
                for each_value in values:
                    if ' ' in each_value:
                        each_key, each_val = re.split(r"\s+", each_value)
                        result[key + ' (' + each_key + ')'] = each_val
                    else:
                        result[key] = value
            else:
                result[key] = value
        # Get the last key-value pair:
        last_match = key_positions[-1]
        key = last_match.group(1)
        value = conditions[last_match.end(0):]
        result[key] = value
        return result

    def is_notice(self):
        return self.event_type in ['INFO', 'DEBUG', 'WARNING', 'ERROR']

    def formatted_value(self, key):
        if hasattr(self, key):
            return str(getattr(self, key))
        elif key in self.conditions:
            value = self.conditions[key]
            if re.match(r"^\d*\.?\d+[VAC]$", value):
                return value[:-1]
            if re.match(r"^\d*\.?\d+mV$", value):
                return str(int(value[:-2]) / 1000)
            return value
        return ''

    def to_csv(self, headers, sep=','):
        return sep.join([self.formatted_value(key) for key in headers])

    def to_tsv(self, headers):
        return self.to_csv(headers, sep='\t')

    def to_json(self):
        return json.dumps({
            'entry': self.entry,
            'timestamp': self.timestamp and str(self.timestamp) or '',
            'component': self.component,
            'event_type': self.event_type,
            'event_level': self.event_level,
            'event': self.event,
            'conditions': self.conditions
        })


class LogFile:
    header: LogHeader
    entries: List[LogEntry]

    common_headers = ['entry',
                      'timestamp',
                      'component',
                      'event_type',
                      'event_level',
                      'event']

    def __init__(self, input_filepath):
        with open(input_filepath) as log_file:
            # Read header:
            self.header = LogHeader(log_file)
            # Read and process log entries:
            self.entries = [LogEntry(line) for line in log_file.readlines()]

    def decorate_entries_with_riding_charging_phases(self):
        pass

    @property
    def all_conditions_keys(self):
        conditions_keys = []
        for entry in self.entries:
            for k in entry.conditions.keys():
                if k not in conditions_keys:
                    conditions_keys.append(k)
        return conditions_keys

    @property
    def headers(self):
        return self.common_headers + self.all_conditions_keys


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
    log = LogFile(log_filepath)

    output_format = args.format
    line_sep = os.linesep
    output_filepath = args.outfile
    if not output_filepath:
        output_filepath = log_filepath + '.' + output_format

    with open(output_filepath, 'w') as output:
        # Write header:
        log_headers = log.headers
        if output_format == 'csv':
            output.write(','.join(log_headers) + line_sep)
        elif output_format == 'tsv':
            output.write('\t'.join(log_headers) + line_sep)
        # Write log entries:
        for log_entry in log.entries:
            if output_format == 'csv':
                output.write(log_entry.to_csv(log_headers) + line_sep)
            elif output_format == 'tsv':
                output.write(log_entry.to_tsv(log_headers) + line_sep)
            elif output_format == 'json':
                output.write(log_entry.to_json() + ',' + line_sep)
