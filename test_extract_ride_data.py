from unittest import TestCase
from extract_ride_data import LogEntry


class TestLogEntry(TestCase):
    def assertLogEntryIsConsistent(self, log_entry: LogEntry):
        self.assertIsInstance(log_entry.entry, int)
        self.assertLess(0, log_entry.entry)
        self.assertIsInstance(log_entry.event, str)
        self.assertIsInstance(log_entry.component, str)
        self.assertIsInstance(log_entry.conditions, dict)

    def test_conditions_to_dict(self):
        conditions = LogEntry.conditions_to_dict(
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
        conditions = LogEntry.conditions_to_dict(
            '''Bmvolts: 92062, Cmvolts: 118937, Amps: 0, RPM: 0''')
        self.assertDictEqual({'Bmvolts': '92062',
                              'Cmvolts': '118937',
                              'Amps': '0',
                              'RPM': '0'},
                             conditions)

    def test_disarmed(self):
        log_entry = LogEntry('''
 00001     05/21/2018 21:12:20   Disarmed                   \
 PackTemp: h 21C, l 20C, PackSOC: 91%, Vpack:113.044V, MotAmps:   0, BattAmps:   2, Mods: 11,\
  MotTemp:  26C, CtrlTemp:  19C, AmbTemp:  20C, MotRPM:   0, Odo:48809km
''')
        self.assertLogEntryIsConsistent(log_entry)
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
        log_entry = LogEntry('''
 07558     05/20/2018 16:36:56   INFO:  Bmvolts: 92062, Cmvolts: 118937, Amps: 0, RPM: 0    
''')
        self.assertLogEntryIsConsistent(log_entry)
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
        log_entry = LogEntry('''
 07544     05/20/2018 16:36:52   DEBUG: Module mode Change Requires Disconnect    
''')
        self.assertLogEntryIsConsistent(log_entry)
        self.assertEqual(7544, log_entry.entry)
        self.assertEqual('DEBUG', log_entry.event_level)
        self.assertEqual('Module mode Change Requires Disconnect', log_entry.event)
        self.assertDictEqual({}, log_entry.conditions)

    def test_current_limited(self):
        log_entry = LogEntry('''
 07396     05/20/2018 16:15:31\
    Batt Dischg Cur Limited    281 A (40.72463768115942%), MinCell: 3383mV, MaxPackTemp: 34C''')
        self.assertLogEntryIsConsistent(log_entry)
        self.assertEqual(7396, log_entry.entry)
        self.assertEqual('LIMIT', log_entry.event_type)
        self.assertEqual('Batt Dischg Cur Limited', log_entry.event)
        self.assertDictEqual({'MinCell': '3383mV',
                              'MaxPackTemp': '34C',
                              'BattAmps': '281',
                              'PackSOC': '40.72463768115942%'},
                             log_entry.conditions)

    def test_error_entry(self):
        log_entry = LogEntry('''
 07758     05/20/2018 16:52:01\
   ERROR: Module 01 maximum connection retries reached. Flagging ineligble.    
''')
        self.assertLogEntryIsConsistent(log_entry)
        self.assertEqual(7758, log_entry.entry)
        self.assertEqual('ERROR', log_entry.event_level)
        self.assertEqual('Battery', log_entry.component)
        self.assertEqual('Module maximum connection retries reached. Flagging ineligble.',
                         log_entry.event)
        self.assertDictEqual({'Module': '01'}, log_entry.conditions)

    def test_module_not_connected(self):
        log_entry = LogEntry('''
 01525     05/14/2018 16:49:14   Module 1 not connected, PV 109511mV, diff 0mV, Allowed diff 750mV,\
 pack cap 26Ah, batt curr 0A, PackTemp h 23C, l 23C, last CAN msg 4ms ago, lcell 3903mV,\
 Max charge 10cx10, max discharge 100cx10
''')
        self.assertLogEntryIsConsistent(log_entry)
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
