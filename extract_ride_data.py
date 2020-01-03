#!/usr/bin/env python3

"""
This extracts data from decoded/text logs for Zero Motorcycles.

It supports CSV/TSV tabular formats as well as JSON.
"""

import os
from collections import namedtuple
from datetime import datetime
import string
import re
import json
from bisect import bisect_right
from typing import List, Tuple, Dict, IO, Optional, Any

from decode_vin import decode_vin


EMPTY_CSV_VALUE = ''


def print_value_tabular(value, omit_units=False):
    """Stringify the value for CSV/TSV; treat None as empty text."""
    if value is None:
        return EMPTY_CSV_VALUE
    if omit_units and value is str:
        matches = re.match(r"^([0-9.]+)\s*([A-Za-z]+)$", value)
        if matches:
            return matches.group(1)
    return str(value)


class LogHeader:
    """Parse and represent the metadata in a log header."""
    log_title: str
    column_labels: List[str]


class LogEntry:
    """Parse and represent the metadata, message, and data in a log entry."""
    timestamp: datetime
    log_tag: Optional[str]
    field_values: Optional[List[str]]
    conditions: Dict[str, str] = {}

    def __init__(self, log_text: str, index=None, verbose=0, field_sep=None):
        if verbose > 1:
            if index is not None:
                print("Reading log entry (line {})".format(index))
            else:
                print("Reading log entry")
        if field_sep:
            self.field_values = [field_value.strip() for field_value in log_text.split(field_sep)]

    @classmethod
    def decode_timestamp(cls, timestamp_text):
        """Parse a timestamp from ISO format."""
        try:
            return datetime.fromisoformat(timestamp_text)
        except ValueError:
            return None

    def __cmp__(self, other):
        """Timestamp order
        :param other: LogEntry
        :returns bool"""
        return self.timestamp.__cmp__(other.timestamp)

    def __lt__(self, other):
        """Timestamp order
        :param other: LogEntry
        :returns bool"""
        return self.timestamp < other.timestamp

    def __gt__(self, other):
        """Timestamp order
        :param other: LogEntry
        :returns bool"""
        return self.timestamp > other.timestamp

    def print_property_tabular(self, index, key, omit_units=False):
        """For tabular output, print a built-in property or condition value."""
        if hasattr(self, key):
            return print_value_tabular(getattr(self, key), omit_units=omit_units)
        if self.field_values:
            return print_value_tabular(self.field_values[index], omit_units=omit_units)
        return EMPTY_CSV_VALUE

    def to_csv(self, headers, field_sep=',', omit_units=False):
        """Produce a tabular output line."""
        return field_sep.join([self.print_property_tabular(index, key, omit_units=omit_units)
                               for index, key in enumerate(headers)])

    def to_tsv(self, headers, omit_units=False):
        """Produce a tabular output line with tab separator."""
        return self.to_csv(headers, field_sep='\t', omit_units=omit_units)

    def to_json(self):
        """Convert to JSON-serializable data structure."""
        return {
            'timestamp': self.timestamp and str(self.timestamp) or ''
        }


class Log:
    """Represent a log as a list of entries."""
    entries: List[LogEntry] = []
    tabular_header_labels: List[str] = []

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable data structure."""
        return {
            'entries': [entry_data.to_json() for entry_data in self.entries]
        }

    def output_to_file(self, output_filepath, output_format,
                       omit_units=False, line_sep=os.linesep, verbose=0):
        """Emit output to the filepath in the given format."""
        if verbose >= 0:
            print('Emitting {} output to: {}'.format(output_format.upper(), output_filepath))
        log_headers = self.tabular_header_labels
        with open(output_filepath, 'w') as output:
            if output_format == 'csv':
                output.write(','.join(log_headers) + line_sep)  # Write header
                for log_entry in self.entries:  # Write entries:
                    output.write(log_entry.to_csv(log_headers, omit_units=omit_units) + line_sep)
            elif output_format == 'tsv':
                output.write('\t'.join(log_headers) + line_sep)  # Write header
                for log_entry in self.entries:  # Write entries:
                    output.write(log_entry.to_tsv(log_headers, omit_units=omit_units) + line_sep)
            elif output_format == 'json':
                output.write(json.dumps(self.to_json(), indent=2))


class LogFile(Log):
    """Parse and represent an entire log file."""
    input_filepath: str
    header: LogHeader = None

    def __init__(self, input_filepath: str, tabular_header_labels=None, verbose=0):
        self.input_filepath = input_filepath
        if tabular_header_labels:
            self.tabular_header_labels = tabular_header_labels
        self.refresh(verbose=verbose)

    def refresh(self, verbose=0):
        """Parse the input file into state."""
        with open(self.input_filepath) as log_file:
            if verbose > 0:
                print("Reading log entries from: {}".format(self.input_filepath))
            self.entries = [LogEntry(line, index=index, verbose=verbose)
                            for index, line in enumerate(log_file.readlines())
                            if line and len(line) > 5]

    def join_log(self, prefix, another_log):
        """Create a joined log object merging the other log into this one.
        :param prefix: str
        :param another_log: LogFile
        :returns JoinedLog"""
        return JoinedLog(self, {prefix: another_log})


ZeroHeaderMBBMetadata = namedtuple('ZeroHeaderMBBMetadata',
                                   ['serial_no', 'vin', 'firmware_rev', 'board_rev', 'model'])

ZeroHeaderBMSMetadata = namedtuple('ZeroHeaderBMSMetadata',
                                   ['serial_no', 'pack_serial_no', 'initial_date'])


def is_log_divider_line(log_line: str) -> bool:
    """The log divider line immediately precedes the log entries."""
    return log_line.startswith('+-----')


class ZeroLogHeader(LogHeader):
    """Parse and represent the metadata in a Zero Motorcycles log header."""
    log_entries_count_actual: int = 0
    log_entries_count_expected: int = 0
    divider_indexes: List[int]
    mbb_metadata: Optional[ZeroHeaderMBBMetadata]
    bms_metadata: Optional[ZeroHeaderBMSMetadata]

    def __init__(self, log_lines: List[str], verbose=0):
        if verbose > 0:
            print("Reading header")
        header_lines = log_lines[0:self.index_of_divider_line(log_lines) + 1]
        self.log_title = header_lines[0].strip()
        if self.log_source == 'MBB':
            self.mbb_metadata = ZeroHeaderMBBMetadata(
                serial_no=self.value_from_lines(header_lines, prefix='Serial number'),
                vin=self.value_from_lines(header_lines, prefix='VIN'),
                firmware_rev=self.value_from_lines(header_lines, prefix='Firmware rev.'),
                board_rev=self.value_from_lines(header_lines, prefix='Board rev.'),
                model=self.value_from_lines(header_lines, prefix='Model'))
            self.model = decode_vin(self.mbb_metadata.vin)\
                if all(c in string.printable for c in self.mbb_metadata.vin) else None
        elif self.log_source == 'BMS':
            initial_date = self.value_from_lines(header_lines, prefix='Initial date')
            self.bms_metadata = ZeroHeaderBMSMetadata(
                serial_no=self.value_from_lines(header_lines, prefix='BMS serial number'),
                pack_serial_no=self.value_from_lines(header_lines, prefix='Pack serial number'),
                initial_date=datetime.strptime(initial_date, '%b %d %Y %H:%M:%S') or initial_date)
        self.log_entries_count_actual, self.log_entries_count_expected = \
            [int(count) for count in re.findall(r"\d+", header_lines[-4])]
        self.divider_indexes = [i for i, letter in enumerate(header_lines[-2]) if letter == '+']
        self.column_labels = [hdg.strip() for hdg in re.split(r"\s\s+", header_lines[-1])]

    @classmethod
    def index_of_divider_line(cls, log_lines: List[str]) -> int:
        """Which line number is the divider line."""
        last_header_line_index = 0
        while not is_log_divider_line(log_lines[last_header_line_index]):
            last_header_line_index += 1
        return last_header_line_index

    @classmethod
    def read_header_lines(cls, log_input_file: IO):
        """Read the header lines in for parsing/initialization."""
        header_lines = [log_input_file.readline()]
        while not is_log_divider_line(header_lines[-1]):
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
        output = {
            'source': self.log_source,
            'title': self.log_title,
            'num_entries': self.log_entries_count_actual,
            'num_entries_expected': self.log_entries_count_expected
        }
        if self.log_source == 'MBB':
            output['mbb'] = {
                'serial_no': self.mbb_metadata.serial_no,
                'vin': self.mbb_metadata.vin,
                'firmware_rev': self.mbb_metadata.firmware_rev,
                'board_rev': self.mbb_metadata.board_rev,
                'model': self.mbb_metadata.model
            }
            output['model'] = self.model
        if self.log_source == 'BMS':
            output['bms'] = {
                'serial_no': self.bms_metadata.serial_no,
                'pack_serial_no': self.bms_metadata.pack_serial_no,
                'initial_date': str(self.bms_metadata.initial_date)
            }
        return output


class ZeroLogEntry(LogEntry):
    """Parse and represent the metadata, message, and data in a Zero Motorcycles log entry."""
    entry: int = 0
    segment_id: int = 0
    segment_activity: str = EMPTY_CSV_VALUE
    event: str = EMPTY_CSV_VALUE
    event_level: str = EMPTY_CSV_VALUE
    event_type: str = EMPTY_CSV_VALUE
    component: str = EMPTY_CSV_VALUE

    curr_limited_message = 'Batt Dischg Cur Limited'
    low_chassis_isolation_message = 'Low Chassis Isolation'

    def __init__(self, log_text, index=None, verbose=0):
        super().__init__(log_text, index=index, verbose=verbose)
        try:
            self.entry = int(log_text[:9].strip())
            timestamp_text = log_text[10:32].strip()
            if timestamp_text:
                try:
                    self.timestamp = self.decode_timestamp(timestamp_text)
                except ValueError:
                    if verbose > 0:
                        print("Unable to parse timestamp: {}".format(timestamp_text))
            message = log_text[33:].strip()
            self.decode_message(message)
        except ValueError:
            print("Decoding line #{} failed from content: {}".format(index, log_text))

    @classmethod
    def decode_timestamp(cls, timestamp_text):
        """Parse a timestamp the way a Zero Motorcycles log formats it."""
        return datetime.strptime(timestamp_text, '%m/%d/%Y %H:%M:%S')

    @classmethod
    def decode_level_from_message(cls, message: str) -> Tuple[str, str]:
        """Extract and strip log level, return level and remainder"""
        event_level = EMPTY_CSV_VALUE
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
        elif ' error' in event_contents:
            event_level = 'ERROR'
        return event_level, event_contents

    event_types_by_prefix = {
        '0x': 'UNKNOWN',
        'Riding': 'RIDING',
        'Charging': 'CHARGING',
        'Enabling': 'ENABLING',
        'Disabling': 'DISABLING',
    }

    event_types_by_suffix = {
        ' Connected': 'CONNECTED',
        ' Disconnected': 'DISCONNECTED',
        ' Link Up': 'CONNECTED',
        ' Link Down': 'DISCONNECTED',
        ' On': 'ON',
        ' Off': 'OFF'
    }

    @classmethod
    def decode_type_from_message(cls, message: str) -> str:
        """Check contents for event type."""
        event_type = EMPTY_CSV_VALUE
        for prefix, event_type_value in cls.event_types_by_prefix.items():
            if message.startswith(prefix):
                event_type = event_type_value
                break
        for suffix, event_type_value in cls.event_types_by_suffix.items():
            if message.endswith(suffix):
                event_type = event_type_value
                break
        if message.startswith('Turning'):
            if 'ON' in message:
                event_type = 'ON'
            elif 'OFF' in message:
                event_type = 'OFF'
        if 'Charging' in message and 'from Charging' not in message:
            event_type = 'CHARGING'
        if 'Limit' in message:
            event_type = 'LIMIT'
        return event_type

    components_by_message_part = {
        'Battery': 'Battery',
        'Sevcon': 'Controller',
        'DCDC': 'DC-DC Converter',
        'Calex': 'Charger',
        'External Chg': 'External Charger',
        'Charger 6': 'Charge Tank'
    }

    @classmethod
    def decode_component_from_message(cls, message: str) -> str:
        """Check contents for components"""
        component = 'MBB'
        if message.startswith('Module '):
            component = 'Battery'
        else:
            for part, component_value in cls.components_by_message_part.items():
                if part in message:
                    component = component_value
                    break
        return component

    module_no_condition_key = 'Module'

    def decode_special_message_conditions(self, event_contents: str) -> str:
        """Identify special conditions in the event contents"""
        if event_contents.startswith(self.curr_limited_message):
            matches = re.search(r"(\d+) A \((\d+\.?\d+%)\)", event_contents)
            if matches:
                self.conditions['BattAmps'] = matches.group(1)
                self.conditions['PackSOC'] = matches.group(2)
                event_contents = self.curr_limited_message
        elif event_contents.startswith(self.low_chassis_isolation_message):
            matches = re.search(r"(\d+ KOhms) to cell (\d+)", event_contents)
            if matches:
                self.conditions['ImpedanceKOhms'] = matches.group(1)
                self.conditions['Cell'] = matches.group(2)
                event_contents = self.low_chassis_isolation_message
        elif re.match(r'Module \d not connected', event_contents):
            module_no = re.findall(r"\d+", event_contents)[0]
            self.conditions[self.module_no_condition_key] = module_no
            condition_parts = event_contents.split(',')[1:]
            for condition_part in condition_parts:
                matches = re.match(r"^(.*)\s+([0-9][A-Za-z0-9]*)$", condition_part)
                if matches:
                    self.conditions[matches.group(1).strip()] = matches.group(2)
            event_contents = 'Module not connected'
        elif re.match(r'Battery module \d+ contactor closed', event_contents):
            module_no = re.findall(r"\d+", event_contents)[0]
            self.conditions[self.module_no_condition_key] = module_no
            event_contents = 'Battery module contactor closed'
        elif re.match(r'Module \d\d', event_contents):
            module_no = re.findall(r"\d+", event_contents)[0]
            self.conditions[self.module_no_condition_key] = module_no
            event_contents = event_contents[:7] + event_contents[10:]
        elif self.component == 'Charge Tank':
            if self.conditions.get('SW') and ' ' in self.conditions['SW']:
                # Example entry for "Charger 6": 'SN:1838032 SW:206 247Vac  62Hz EVSE 41A'
                sw_conditions = self.conditions['SW'].split()
                self.conditions['SW'] = sw_conditions[0]
                self.conditions['EVSE Voltage'] = sw_conditions[1]
                self.conditions['EVSE Frequency'] = sw_conditions[2]
                self.conditions['EVSE Amps'] = sw_conditions[4]
        return event_contents

    def decode_message(self, message: str):
        """Extract LogEntry properties from the log text after the timestamp."""
        self.event_level, event_contents = self.decode_level_from_message(message)

        self.event_type = self.decode_type_from_message(event_contents)
        if self.event_type == 'UNKNOWN':
            event_contents = EMPTY_CSV_VALUE

        self.component = self.decode_component_from_message(event_contents)

        # Identify and parse out conditions data:
        first_keyword_match = re.search(r"[A-Za-z]+:", event_contents)
        if first_keyword_match:
            idx = first_keyword_match.start(0)
            conditions_field = event_contents[idx:].strip()
            event_contents = event_contents[:idx].strip()
            self.conditions = self.conditions_to_dict(conditions_field)
        else:
            self.conditions = {}

        event_contents = self.decode_special_message_conditions(event_contents)

        self.event = event_contents

    @classmethod
    def conditions_to_dict(cls, conditions: str) -> dict:
        """Extract key-value data pairs in the message and conditions text."""
        result = {}
        key_positions = list(re.finditer(r",?\s*([A-Za-z]+\s*[A-Za-z]*):\s*", conditions))
        for i, j in zip(key_positions[0::1], key_positions[1::1]):
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
        """Whether the event has a log level."""
        return self.event_level in ['INFO', 'DEBUG', 'WARNING', 'ERROR']

    def is_battery_event(self):
        """Whether the event is battery-related."""
        return self.component == 'Battery'

    def battery_module_no(self) -> Optional[int]:
        """Which battery module, if any, is involved."""
        if self.is_battery_event():
            return int(self.conditions[self.module_no_condition_key])
        return None

    def is_contactor_close_entry(self) -> bool:
        """Whether the event means the/a contactor is closing."""
        return (self.is_battery_event() and self.event == 'Module Closing Contactor'
                and self.battery_module_no() == 0)

    def is_contactor_open_entry(self) -> bool:
        """Whether the event means the/a contactor is closing."""
        return (self.is_battery_event() and self.event == 'Module Opening Contactor'
                and self.battery_module_no() == 0)

    def is_running_entry(self) -> bool:
        """Whether the event is a riding event."""
        return self.event_type == 'RIDING'

    def is_charging_entry(self) -> bool:
        """Whether the event is a charging event."""
        return self.event_type == 'CHARGING'

    def print_property_tabular(self, index, key, omit_units=False):
        """For tabular output, print a built-in property or condition value."""
        if hasattr(self, key):
            return print_value_tabular(getattr(self, key), omit_units=omit_units)
        if key in self.conditions:
            value = self.conditions[key]
            if re.match(r"^\d*\.?\d+[VAC]$", value):
                return value[:-1]
            if re.match(r"^\d*\.?\d+mV$", value):
                return print_value_tabular(int(value[:-2]) / 1000, omit_units=omit_units)
            return value
        return EMPTY_CSV_VALUE

    def to_json(self):
        """Convert to JSON-serializable data structure."""
        return {
            'entry': self.entry or None,
            'segment_id': self.segment_id,
            'segment_activity': self.segment_activity,
            'timestamp': hasattr(self, 'timestamp') and str(self.timestamp) or '',
            'component': self.component,
            'event_type': self.event_type,
            'event_level': self.event_level,
            'event': self.event,
            'conditions': self.conditions
        }


class ZeroLogFile(LogFile):
    """Parse and represent an entire Zero Motorcycles log file."""
    header: ZeroLogHeader
    entries: List[ZeroLogEntry] = []

    common_headers = ['entry',
                      'segment_id',
                      'segment_activity',
                      'timestamp',
                      'component',
                      'event_type',
                      'event_level',
                      'event']

    def annotate_entry_segment_info(self):
        """Auto-increment a numeric ID for each sequence of entries for a closed contactor."""
        current_segment_id = 0
        current_activity = 'STOPPED'
        for entry in self.entries:
            if entry.is_contactor_close_entry():
                current_activity = 'STARTED'
                current_segment_id += 1
            elif entry.is_contactor_open_entry():
                current_activity = 'STOPPED'
                current_segment_id += 1
            elif entry.is_running_entry() and current_activity != 'RIDING':
                current_activity = 'RIDING'
                current_segment_id += 1
            elif entry.is_charging_entry() and current_activity != 'CHARGING':
                current_activity = 'CHARGING'
                current_segment_id += 1
            entry.segment_id = current_segment_id
            entry.segment_activity = current_activity

    def refresh(self, verbose=0):
        """Parse the input file into state."""
        with open(self.input_filepath) as log_file:
            if verbose > 0:
                print("Reading log header from: {}".format(self.input_filepath))
            log_lines = log_file.readlines()
            self.header = ZeroLogHeader(log_lines, verbose=verbose)
        if verbose > 0:
            print("Reading log entries from: {}".format(self.input_filepath))
        divider_index = self.header.index_of_divider_line(log_lines)
        self.entries = [ZeroLogEntry(line, index=index, verbose=verbose)
                        for index, line in enumerate(log_lines)
                        if index > divider_index and line and len(line) > 5]
        self.annotate_entry_segment_info()
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
        output = {'header': self.header.to_json()}
        output.update(super().to_json())
        return output


class JoinedLog(Log):
    """This represents the joining or aggregation of two or more LogFiles."""
    secondary_logs: Dict[str, LogFile]
    primary_log: LogFile
    sorted_entries: List[LogEntry]

    def __init__(self, primary_log: LogFile, secondary_logs: Dict[str, LogFile]):
        self.primary_log = primary_log
        self.secondary_logs = secondary_logs
        self.refresh()

    @property
    def all_entries_by_timestamp(self) -> List[LogEntry]:
        """Return each LogEntry in turn, by timestamp order."""
        all_entries = self.primary_log.entries
        for key, log in self.secondary_logs.items():
            for entry in log.entries:
                entry.log_tag = key
            all_entries.extend(log.entries)
        all_entries.sort(key=lambda log_entry: log_entry.timestamp)
        return all_entries

    @property
    def entries(self):
        """Alias sorted_entries for now. Might be synthetic later."""
        return self.sorted_entries

    def refresh(self, deep=False, verbose=0):
        """Update state from inputs."""
        if verbose > 0:
            print("Refreshing joined log")
        if deep:
            self.primary_log.refresh(verbose=verbose)
            for log in self.secondary_logs.values():
                log.refresh(verbose=verbose)
        self.sorted_entries = self.all_entries_by_timestamp

    def entry_for_timestamp(self, when: datetime) -> LogEntry:
        """Synthesize a merged log entry for the given timestamp."""
        dummy_entry = LogEntry('')
        dummy_entry.timestamp = when
        entry_index = bisect_right(self.sorted_entries, dummy_entry)
        return self.sorted_entries[entry_index]

    @staticmethod
    def entry_to_json(log_entry: LogEntry) -> Dict[str, str]:
        """Convert entry to JSON-serializable data structure, tagging key as LogSource."""
        output = log_entry.to_json()
        if log_entry.log_tag:
            output['LogTag'] = log_entry.log_tag
        return output

    def to_json(self):
        """Convert to JSON-serializable data structure."""
        return {
            'entries': [self.entry_to_json(entry_data) for entry_data in self.entries]
        }

    def join_log(self, prefix, another_log):
        """Create a joined log object merging the other log into this one.
        :param prefix: str
        :param another_log: LogFile
        :returns JoinedLog"""
        secondary_logs = self.secondary_logs.copy()
        secondary_logs[prefix] = another_log
        return self.__class__(self.primary_log, secondary_logs)


if __name__ == "__main__":
    import sys
    import argparse

    ARGS_PARSER = argparse.ArgumentParser()
    ARGS_PARSER.add_argument("--format", default='all',
                             choices=['csv', 'tsv', 'json', 'all'],
                             help="the output format desired")
    ARGS_PARSER.add_argument("--verbose", "-v",
                             action='count', default=0,
                             help="show more processing details")
    ARGS_PARSER.add_argument("--omit-units",
                             action='store_true', dest='omit_units',
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
    LOG_FILE = ZeroLogFile(LOG_FILEPATH, verbose=CLI_ARGS.verbose)

    OUTPUT_FORMAT = CLI_ARGS.format

    OMIT_UNITS = CLI_ARGS.omit_units

    OUTPUT_FILEPATH = CLI_ARGS.outfile
    if OUTPUT_FILEPATH:
        BASE_FILEPATH = os.path.splitext(OUTPUT_FILEPATH)[0]
    else:
        BASE_FILEPATH = os.path.splitext(LOG_FILEPATH)[0]
        OUTPUT_FILEPATH = BASE_FILEPATH + '.' + OUTPUT_FORMAT

    if OUTPUT_FORMAT == 'all':
        for out_format in ['csv', 'tsv', 'json']:
            out_filepath = BASE_FILEPATH + '.' + out_format
            LOG_FILE.output_to_file(out_filepath, out_format, omit_units=OMIT_UNITS)
    else:
        LOG_FILE.output_to_file(OUTPUT_FILEPATH, OUTPUT_FORMAT, omit_units=OMIT_UNITS)
