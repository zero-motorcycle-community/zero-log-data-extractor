from unittest import TestCase
from datetime import datetime
from extract_ride_data import ZeroLogHeader, LogEntry, ZeroLogEntry


class TestLogHeader(TestCase):
    def test_decode(self):
        log_text = '''Zero MBB log

Serial number      2015_mbb_48e0f7_00720
VIN                538SD9Z37GCG06073
Firmware rev.      51
Board rev.         3
Model              DSR

Printing 8397 of 8397 log entries..

 Entry    Time of Log            Event                      Conditions
+--------+----------------------+--------------------------+----------------------------------
 00001     05/13/2018 10:06:43   DEBUG: Sevcon Contactor Drive ON.
'''
        log_lines = log_text.splitlines()
        log_header = ZeroLogHeader(log_lines)
        self.assertEqual({
            'mbb': {
                'board_rev': '3',
                'firmware_rev': '51',
                'model': 'DSR',
                'serial_no': '2015_mbb_48e0f7_00720',
                'vin': '538SD9Z37GCG06073'},
            'model': {'manufacturer': 'Zero Motorcycles',
                      'model': 'DSR',
                      'motor': {'power': '16kW', 'size': '75-7R'},
                      'pack_capacity': '13.0',
                      'plant_location': 'Santa Cruz, CA',
                      'platform': 'SDS',
                      'year': 2016},
            'num_entries': 8397,
            'num_entries_expected': 8397,
            'source': 'MBB',
            'title': 'Zero MBB log'
        }, log_header.to_json())


class TestLogEntry(TestCase):
    def test_decode(self):
        log_entry = LogEntry(' 2018-05-20 16:36:56 \t   something happened   \n', field_sep='\t')
        self.assertEqual(log_entry.field_values, ['2018-05-20 16:36:56', 'something happened'])

    def test_order(self):
        first_entry = LogEntry('2018-05-20 16:36:56\tsomething happened', field_sep='\t')
        first_entry.timestamp = first_entry.decode_timestamp(first_entry.field_values[0])
        second_entry = LogEntry('2018-05-20 16:37:00\tsomething happened later', field_sep='\t')
        second_entry.timestamp = second_entry.decode_timestamp(second_entry.field_values[0])
        self.assertLess(first_entry, second_entry)
        self.assertGreater(second_entry, first_entry)

    def test_to_csv(self):
        log_entry = LogEntry('  2018-05-20 16:36:56 \t  something happened   \n', field_sep='\t')
        self.assertEqual('2018-05-20 16:36:56,something happened',
                         log_entry.to_csv(['timestamp', 'message']))


class TestZeroLogEntry(TestCase):
    def assert_consistent_log_entry(self, log_entry: ZeroLogEntry):
        self.assertIsInstance(log_entry.entry, int)
        self.assertIsInstance(log_entry.timestamp, datetime)
        self.assertLess(0, log_entry.entry)
        self.assertIsInstance(log_entry.event, str)
        self.assertIsInstance(log_entry.component, str)
        self.assertIsInstance(log_entry.conditions, dict)

    def test_conditions_to_dict(self):
        conditions = ZeroLogEntry.conditions_to_dict(
            '''PackTemp: h 21C, l 20C, PackSOC: 91%, Vpack:113.044V, MotAmps:   0, BattAmps:   2,\
             Mods: 11,  MotTemp:  26C, CtrlTemp:  19C, AmbTemp:  20C, MotRPM:   0, Odo:48809km'''
        )
        self.assertDictEqual({'AmbTemp': '20C',
                              'BattAmps': '2',
                              'CtrlTemp': '19C',
                              'Mods': '11',
                              'MotAmps': '0',
                              'MotRPM': '0',
                              'MotTemp': '26C',
                              'Odo': '48809km',
                              'PackSOC': '91%',
                              'PackTemp (h)': '21C',
                              'PackTemp (l)': '20C',
                              'Vpack': '113.044V'}, conditions)
        conditions = ZeroLogEntry.conditions_to_dict(
            '''Bmvolts: 92062, Cmvolts: 118937, Amps: 0, RPM: 0''')
        self.assertDictEqual({'Bmvolts': '92062',
                              'Cmvolts': '118937',
                              'Amps': '0',
                              'RPM': '0'},
                             conditions)

    def test_disarmed(self):
        log_entry = ZeroLogEntry('''
 00001     05/21/2018 21:12:20   Disarmed                   \
 PackTemp: h 21C, l 20C, PackSOC: 91%, Vpack:113.044V, MotAmps:   0, BattAmps:   2, Mods: 11,\
  MotTemp:  26C, CtrlTemp:  19C, AmbTemp:  20C, MotRPM:   0, Odo:48809km
''')
        self.assert_consistent_log_entry(log_entry)
        self.assertEqual(1, log_entry.entry)
        self.assertEqual('', log_entry.event_type)
        self.assertEqual('', log_entry.event_level)
        self.assertEqual('Disarmed', log_entry.event)
        self.assertDictEqual({'AmbTemp': '20C',
                              'BattAmps': '2',
                              'CtrlTemp': '19C',
                              'Mods': '11',
                              'MotAmps': '0',
                              'MotRPM': '0',
                              'MotTemp': '26C',
                              'Odo': '48809km',
                              'PackSOC': '91%',
                              'PackTemp (h)': '21C',
                              'PackTemp (l)': '20C',
                              'Vpack': '113.044V'},
                             log_entry.conditions)

    def test_info_only_data(self):
        log_entry = ZeroLogEntry('''
 07558     05/20/2018 16:36:56   INFO:  Bmvolts: 92062, Cmvolts: 118937, Amps: 0, RPM: 0    
''')
        self.assert_consistent_log_entry(log_entry)
        self.assertEqual(7558, log_entry.entry)
        self.assertEqual('2018-05-20 16:36:56', str(log_entry.timestamp))
        self.assertEqual('INFO', log_entry.event_level)
        self.assertEqual('', log_entry.event)
        self.assertDictEqual({'Bmvolts': '92062',
                              'Cmvolts': '118937',
                              'Amps': '0',
                              'RPM': '0'},
                             log_entry.conditions)

    def test_info_and_conditions_message_join(self):
        log_entry = ZeroLogEntry('''
 07544     05/20/2018 16:36:52   DEBUG: Module mode Change Requires Disconnect    
''')
        self.assert_consistent_log_entry(log_entry)
        self.assertEqual(7544, log_entry.entry)
        self.assertEqual('DEBUG', log_entry.event_level)
        self.assertEqual('Module mode Change Requires Disconnect', log_entry.event)
        self.assertDictEqual({}, log_entry.conditions)

    def test_current_limited(self):
        log_entry = ZeroLogEntry('''
 07396     05/20/2018 16:15:31\
    Batt Dischg Cur Limited    281 A (40.72463768115942%), MinCell: 3383mV, MaxPackTemp: 34C''')
        self.assert_consistent_log_entry(log_entry)
        self.assertEqual(7396, log_entry.entry)
        self.assertEqual('LIMIT', log_entry.event_type)
        self.assertEqual('Batt Dischg Cur Limited', log_entry.event)
        self.assertDictEqual({'MinCell': '3383mV',
                              'MaxPackTemp': '34C',
                              'BattAmps': '281',
                              'PackSOC': '40.72463768115942%'},
                             log_entry.conditions)

    def test_error_entry(self):
        log_entry = ZeroLogEntry('''
 07758     05/20/2018 16:52:01\
   ERROR: Module 01 maximum connection retries reached. Flagging ineligble.    
''')
        self.assert_consistent_log_entry(log_entry)
        self.assertEqual(7758, log_entry.entry)
        self.assertEqual('ERROR', log_entry.event_level)
        self.assertEqual('Battery', log_entry.component)
        self.assertTrue(log_entry.is_battery_event())
        self.assertEqual('Module maximum connection retries reached. Flagging ineligble.',
                         log_entry.event)
        self.assertDictEqual({'Module': '01'}, log_entry.conditions)
        self.assertEqual(1, log_entry.battery_module_no())

    def test_module_not_connected(self):
        log_entry = ZeroLogEntry('''
 01525     05/14/2018 16:49:14   Module 1 not connected, PV 109511mV, diff 0mV, Allowed diff 750mV,\
 pack cap 26Ah, batt curr 0A, PackTemp h 23C, l 23C, last CAN msg 4ms ago, lcell 3903mV,\
 Max charge 10cx10, max discharge 100cx10
''')
        self.assert_consistent_log_entry(log_entry)
        self.assertEqual(1525, log_entry.entry)
        self.assertEqual({'Module': '1',
                          'PV': '109511mV',
                          'diff': '0mV',
                          'Allowed diff': '750mV',
                          'pack cap': '26Ah',
                          'batt curr': '0A',
                          'PackTemp h': '23C',
                          'l': '23C',
                          'lcell': '3903mV',
                          'Max charge': '10cx10',
                          'max discharge': '100cx10'},
                         log_entry.conditions)
        self.assertEqual(1, log_entry.battery_module_no())
