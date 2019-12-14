#!/usr/bin/env python3

import os
from datetime import datetime
import argparse
import json


class LogHeader():
    def __init__(self, log_file):
        self.log_title = log_file.readline()
        log_file.readline()
        self.serial_no = log_file.readline()
        self.vin = log_file.readline()
        self.firmware_rev = log_file.readline()
        self.board_rev = log_file.readline()
        self.model = log_file.readline()
        log_file.readline()
        self.log_entries_count = log_file.readline()
        log_file.readline()
        self.column_headings = log_file.readline()
        self.column_divider = log_file.readline()


class LogEntry():
    def __init__(self, log_text):
        try:
            self.entry = int(log_text[:9].strip())
            timestamp_text = log_text[10:32].strip()
            if timestamp_text:
                try:
                    self.timestamp = datetime.strptime(timestamp_text, '%m/%d/%Y %H:%M:%S')
                except ValueError:
                    self.timestamp = None
            self.event = log_text[33:].strip()
            self.conditions = None
            if self.has_conditions():
                self.event = log_text[33:59].strip()
                self.conditions = log_text[60:].strip()
        except Exception as e:
            print(log_text)
            raise e

    def is_notice(self):
        return (self.event.startswith('INFO:') or
                self.event.startswith('DEBUG:') or
                self.event.startswith('WARNING:'))

    def has_conditions(self):
        return not self.is_notice()

    def is_ride_entry(self):
        return self.entry == 'Riding'

    def is_charge_entry(self):
        return self.entry == 'Charging'

    def to_csv(self, sep=','):
        return sep.join([
            str(self.entry),
            self.timestamp and str(self.timestamp) or '',
            self.event,
            self.conditions and self.conditions or ''])

    def to_tsv(self):
        return self.to_csv(sep='\t')

    def to_json(self):
        return json.dumps({
            'entry': self.entry,
            'timestamp': self.timestamp and str(self.timestamp) or '',
            'event': self.event,
            'conditions': self.conditions
        })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", default='tsv',
                        help="the output format desired: csv,tsv,json")
    parser.add_argument("logfile",
                        help="the parsed log file to process")

    args = parser.parse_args()
    log_filepath = args.logfile
    if not os.path.exists(log_filepath):
        print("Log file does not exist: ", log_filepath)
        exit(1)
    output_format = args.format
    line_sep = os.linesep

    with open(log_filepath) as log_file:
        header_info = LogHeader(log_file)
        with open("output.csv", 'w') as output:
            line = log_file.readline()
            while line:
                log_entry = LogEntry(line)
                if output_format == "csv":
                    output.write(log_entry.to_csv() + line_sep)
                elif output_format == "tsv":
                    output.write(log_entry.to_tsv() + line_sep)
                elif output_format == "json":
                    output.write(log_entry.to_json() + ',' + line_sep)
                line = log_file.readline()
