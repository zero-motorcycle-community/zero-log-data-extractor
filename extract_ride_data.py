#!/usr/bin/env python3

"""
This extracts data from decoded/text logs for Zero Motorcycles.

It supports CSV/TSV tabular formats as well as JSON.
"""

import os
from collections import namedtuple
from datetime import datetime
import re
import json
from typing import List, Tuple, Dict, IO, Optional, Union


def print_value_tabular(value):
    """Stringify the value for CSV/TSV; treat None as empty text."""
    if value is None:
        return ''
    return str(value)


MBBHeaderMetadata = namedtuple('MBBHeaderMetadata',
                               ['serial_no', 'vin', 'firmware_rev', 'board_rev', 'model'])

BMSHeaderMetadata = namedtuple('BMSHeaderMetadata',
                               ['serial_no', 'pack_serial_no', 'initial_date'])


class LogHeader:
    """Parse and represent the metadata in a Zero Motorcycles log header."""
    log_title: str
    log_entries_count: List[int]
    divider_indexes: List[int]
    column_labels: List[str]
    mbb_metadata: MBBHeaderMetadata
    bms_metadata: BMSHeaderMetadata

    def __init__(self, log_input_file: IO, verbose=0):
        if verbose > 0:
            print("Reading header")
        header_lines = self.read_header_lines(log_input_file)
        self.log_title = header_lines[0].strip()
        if self.log_source == 'MBB':
            serial_no = self.value_from_lines(header_lines, prefix='Serial number')
            vin = self.value_from_lines(header_lines, prefix='VIN')
            firmware_rev = self.value_from_lines(header_lines, prefix='Firmware rev.')
            board_rev = self.value_from_lines(header_lines, prefix='Board rev.')
            model = self.value_from_lines(header_lines, prefix='Model')
            self.mbb_metadata = MBBHeaderMetadata(
                serial_no=serial_no,
                vin=vin,
                firmware_rev=firmware_rev,
                board_rev=board_rev,
                model=model)
        elif self.log_source == 'BMS':
            initial_date = self.value_from_lines(header_lines, prefix='Initial date')
            serial_no = self.value_from_lines(header_lines, prefix='BMS serial number')
            pack_serial_no = self.value_from_lines(header_lines, prefix='Pack serial number')
            self.bms_metadata = BMSHeaderMetadata(
                serial_no=serial_no,
                pack_serial_no=pack_serial_no,
                initial_date=datetime.strptime(initial_date, '%b %d %Y %H:%M:%S') or initial_date)
        self.log_entries_count = [int(count)
                                  for count in re.findall(r"\d+", header_lines[-3])]
        self.divider_indexes = [i for i, letter in enumerate(header_lines[-1]) if letter == '+']
        self.column_labels = [hdg.strip() for hdg in re.split(r"\s\s+", header_lines[-2])]

    @classmethod
    def read_header_lines(cls, log_input_file: IO):
        """Read the header lines in for parsing/initialization."""
        header_lines = [log_input_file.readline()]
        while not header_lines[-1].startswith('+-----'):
            header_lines.append(log_input_file.readline().strip())
        return header_lines

    @classmethod
    def value_from_line(cls, header_line: str, prefix=None) -> str:
        """Return the value indicated in the given header line.
        Header lines have a multi-space separator between label and value."""
        if prefix:
            return header_line[len(prefix):].strip()
        return re.split(r"\s\s+", header_line.strip())[-1]

    @classmethod
    def value_from_lines(cls, header_lines: List[str], prefix: str) -> Optional[str]:
        """Find the header line with the prefix, and return the labeled value"""
        for header_line in header_lines:
            if header_line.startswith(prefix):
                return cls.value_from_line(header_line, prefix=prefix)
        return None

    @property
    def log_source(self):
        """Identify whether a MBB or BMS log."""
        if 'MBB' in self.log_title:
            return 'MBB'
        if 'BMS' in self.log_title:
            return 'BMS'
        return None

    def to_json(self):
        """Convert to JSON-serializable data structure."""
        if self.log_source == 'MBB':
            return {
                'source': self.log_source,
                'title': self.log_title,
                'serial_no': self.mbb_metadata.serial_no,
                'vin': self.mbb_metadata.vin,
                'firmware_rev': self.mbb_metadata.firmware_rev,
                'board_rev': self.mbb_metadata.board_rev,
                'model': self.mbb_metadata.model,
                'num_entries': self.log_entries_count
            }
        if self.log_source == 'BMS':
            return {
                'source': self.log_source,
                'title': self.log_title,
                'serial_no': self.bms_metadata.serial_no,
                'pack_serial_no': self.bms_metadata.pack_serial_no,
                'initial_date': str(self.bms_metadata.initial_date)
            }
        return None


class LogEntry:
    """Parse and represent the metadata, message, and data in a Zero Motorcycles log entry."""
    entry: int = 0
    timestamp: Union[str, datetime] = ''
    event: str = ''
    event_level: str = ''
    event_type: str = ''
    component: str = ''
    conditions: Dict[str, str] = {}

    def __init__(self, log_text, index=None, verbose=0):
        try:
            if verbose > 1:
                print("Reading log entry (line {})".format(index))
            self.entry = int(log_text[:9].strip())
            timestamp_text = log_text[10:32].strip()
            if timestamp_text:
                try:
                    self.timestamp = datetime.strptime(timestamp_text, '%m/%d/%Y %H:%M:%S')
                except ValueError:
                    self.timestamp = ''
            message = log_text[33:].strip()
            for key, value in self.decode_message(message).items():
                setattr(self, key, value)
        except ValueError:
            print("Decoding line #{} failed from content: {}".format(index, log_text))

    @classmethod
    def decode_level_from_message(cls, message: str) -> Tuple[str, str]:
        """Extract and strip log level, return level and remainder"""
        event_level = ''
        event_contents = message
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
        return event_level, event_contents

    @classmethod
    def decode_type_from_message(cls, message: str) -> str:
        """Check contents for event type."""
        event_type = ''
        if message.startswith('0x'):
            event_type = 'UNKNOWN'
        if message.startswith('Riding'):
            event_type = 'RIDING'
        if message.startswith('Charging'):
            event_type = 'CHARGING'
        if message.endswith(' Connected') or message.endswith('Link Up'):
            event_type = 'CONNECTED'
        if message.endswith(' Disconnected') or message.endswith('Link Down'):
            event_type = 'DISCONNECTED'
        if message.endswith(' On') or ' On ' in message:
            event_type = 'ON'
        if message.endswith(' Off') or ' Off ' in message:
            event_type = 'OFF'
        if 'Limit' in message:
            event_type = 'LIMIT'
        return event_type

    @classmethod
    def decode_message(cls, message: str) -> Dict[str, str]:
        """Extract LogEntry properties from the log text after the timestamp."""
        component = 'MBB'
        conditions = {}

        event_level, event_contents = cls.decode_level_from_message(message)

        event_type = cls.decode_type_from_message(event_contents)
        if event_type == 'UNKNOWN':
            event_contents = ''

        # Check contents for components:
        if event_contents.startswith('Module ') or 'Battery' in event_contents:
            component = 'Battery'
        elif 'Sevcon' in event_contents:
            component = 'Controller'
        elif 'Calex' in event_contents:
            component = 'Charger'
        elif 'External Chg' in event_contents:
            component = 'External Charger'

        # Identify and parse out conditions data:
        first_keyword_match = re.search(r"[A-Za-z]+:", event_contents)
        if first_keyword_match:
            idx = first_keyword_match.start(0)
            conditions_field = event_contents[idx:].strip()
            event_contents = event_contents[:idx].strip()
            conditions = cls.conditions_to_dict(conditions_field)

        # Identify special conditions in the event contents:
        curr_limited_message = 'Batt Dischg Cur Limited'
        if event_contents.startswith(curr_limited_message):
            matches = re.search(r"(\d+) A \((\d+\.?\d+%)\)", event_contents)
            if matches:
                conditions['BattAmps'] = matches.group(1)
                conditions['PackSOC'] = matches.group(2)
                event_contents = curr_limited_message
        low_chassis_isolation_message = 'Low Chassis Isolation'
        if event_contents.startswith(low_chassis_isolation_message):
            matches = re.search(r"(\d+ KOhms) to cell (\d+)", event_contents)
            if matches:
                conditions['ImpedanceKOhms'] = matches.group(1)
                conditions['Cell'] = matches.group(2)
                event_contents = low_chassis_isolation_message

        return {'event_type': event_type,
                'event_level': event_level,
                'component': component,
                'event': event_contents,
                'conditions': conditions}

    @classmethod
    def conditions_to_dict(cls, conditions: str) -> dict:
        """Extract key-value data pairs in the message and conditions text."""
        result = {}
        key_positions = list(re.finditer(r",?\s*([A-Za-z]+\s*[A-Za-z]*):\s*", conditions))
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

    def has_log_level(self):
        """Return whether the event has a log level."""
        return self.event_level in ['INFO', 'DEBUG', 'WARNING', 'ERROR']

    def print_property_tabular(self, key):
        """For tabular output, print a built-in property or condition value."""
        if hasattr(self, key):
            return print_value_tabular(getattr(self, key))
        if key in self.conditions:
            value = self.conditions[key]
            if re.match(r"^\d*\.?\d+[VAC]$", value):
                return value[:-1]
            if re.match(r"^\d*\.?\d+mV$", value):
                return print_value_tabular(int(value[:-2]) / 1000)
            return value
        return ''

    def to_csv(self, headers, sep=','):
        """Produce a tabular output line."""
        return sep.join([self.print_property_tabular(key) for key in headers])

    def to_tsv(self, headers):
        """Produce a tabular output line with tab separator."""
        return self.to_csv(headers, sep='\t')

    def to_json(self):
        """Convert to JSON-serializable data structure."""
        return {
            'entry': self.entry or None,
            'timestamp': self.timestamp and str(self.timestamp) or '',
            'component': self.component,
            'event_type': self.event_type,
            'event_level': self.event_level,
            'event': self.event,
            'conditions': self.conditions
        }


class LogFile:
    """Parse and represent an entire log file."""
    header: LogHeader
    entries: List[LogEntry] = []
    tabular_header_labels: List[str] = []

    common_headers = ['entry',
                      'timestamp',
                      'component',
                      'event_type',
                      'event_level',
                      'event']

    def __init__(self, input_filepath: str, verbose=0):
        self.input_filepath = input_filepath
        self.init_from_input_file(verbose=verbose)

    def init_from_input_file(self, verbose=0):
        """Parse the input file into state."""
        with open(self.input_filepath) as log_file:
            # Read header:
            self.header = LogHeader(log_file, verbose=verbose)
            # Read and process log entries:
            if verbose > 0:
                print("Reading log entries")
            self.entries = [LogEntry(line, index=index, verbose=verbose)
                            for index, line in enumerate(log_file.readlines())
                            if line and len(line) > 5]
        self.tabular_header_labels = self.common_headers + self.all_conditions_keys

    @property
    def all_conditions_keys(self):
        """Return data labels used across all log entries for tabular output."""
        conditions_keys = []
        for entry in self.entries:
            for k in entry.conditions.keys():
                if k not in conditions_keys:
                    conditions_keys.append(k)
        return conditions_keys

    def to_json(self):
        """Convert to JSON-serializable data structure."""
        return {
            'header': self.header.to_json(),
            'entries': [entry_data.to_json() for entry_data in self.entries]
        }

    def output_to_file(self, output_filepath, output_format, line_sep=os.linesep):
        """Emit output to the filepath in the given format."""
        log_headers = self.tabular_header_labels
        with open(output_filepath, 'w') as output:
            if output_format == 'csv':
                output.write(','.join(log_headers) + line_sep)  # Write header
                for log_entry in self.entries:  # Write entries:
                    output.write(log_entry.to_csv(log_headers) + line_sep)
            elif output_format == 'tsv':
                output.write('\t'.join(log_headers) + line_sep)  # Write header
                for log_entry in self.entries:  # Write entries:
                    output.write(log_entry.to_tsv(log_headers) + line_sep)
            elif output_format == 'json':
                output.write(json.dumps(self.to_json(), indent=2))


if __name__ == "__main__":
    import sys
    import argparse

    ARGS_PARSER = argparse.ArgumentParser()
    ARGS_PARSER.add_argument("--format", default='tsv',
                             choices=['csv', 'tsv', 'json'],
                             help="the output format desired")
    ARGS_PARSER.add_argument("--verbose", "-v",
                             action='count', default=0,
                             help="show more processing details")
    ARGS_PARSER.add_argument("--omit-units",
                             action='store_true',
                             help="omit units from the data values")
    ARGS_PARSER.add_argument("logfile",
                             help="the parsed log file to process")
    ARGS_PARSER.add_argument("--outfile",
                             help="the name of output file to emit")

    CLI_ARGS = ARGS_PARSER.parse_args()
    LOG_FILEPATH = CLI_ARGS.logfile
    if not os.path.exists(LOG_FILEPATH):
        print("Log file does not exist: ", LOG_FILEPATH)
        sys.exit(1)
    print('Reading log: {}'.format(LOG_FILEPATH))
    LOG_FILE = LogFile(LOG_FILEPATH, verbose=CLI_ARGS.verbose)

    OUTPUT_FORMAT = CLI_ARGS.format
    OUTPUT_FILEPATH = CLI_ARGS.outfile
    if not OUTPUT_FILEPATH:
        OUTPUT_FILEPATH = os.path.splitext(LOG_FILEPATH)[0] + '.' + OUTPUT_FORMAT

    OMIT_UNITS = CLI_ARGS.omit_units
    print('Emitting output to: {}'.format(OUTPUT_FILEPATH))
    LOG_FILE.output_to_file(OUTPUT_FILEPATH, OUTPUT_FORMAT)
