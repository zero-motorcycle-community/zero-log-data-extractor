from unittest import TestCase
from extract_ride_data import LogEntry


class TestLogEntry(TestCase):
    def test_disarmed(self):
        entry = LogEntry('''
 00001     05/21/2018 21:12:20   Disarmed                   \
 PackTemp: h 21C, l 20C, PackSOC: 91%, Vpack:113.044V, MotAmps:   0, BattAmps:   2, Mods: 11,\
  MotTemp:  26C, CtrlTemp:  19C, AmbTemp:  20C, MotRPM:   0, Odo:48809km
''')
        self.assertEqual(1, entry.entry)
        self.assertEqual('', entry.event_type)
        self.assertEqual('', entry.event_level)
        self.assertEqual('Disarmed', entry.event)
        self.assertDictEqual({'AmbTemp': '20C',
                              'BattAmps': '2',
                              'MotTemp': '26C',
                              'Odo': '48809km',
                              'PackTemp (h)': '21C',
                              'PackTemp (l)': '20C',
                              'Vpack': '113.044V'},
                             entry.conditions)

    def test_info_only_data(self):
        entry = LogEntry('''
 07558     05/20/2018 16:36:56   INFO:  Bmvolts: 92062, Cmvolts: 118937, Amps: 0, RPM: 0    
''')
        self.assertEqual(7558, entry.entry)
        self.assertEqual('2018-05-20 16:36:56', str(entry.timestamp))
        self.assertEqual('INFO', entry.event_level)
        self.assertEqual('', entry.event)
        self.assertDictEqual({'Bmvolts': '92062',
                              # FIXME 'Cmvolts': '118937',
                              'Amps': '0',
                              'RPM': '0'},
                             entry.conditions)

    def test_info_and_conditions_message_join(self):
        entry = LogEntry('''
 07544     05/20/2018 16:36:52   DEBUG: Module mode Change Requires Disconnect    
''')
        self.assertEqual(7544, entry.entry)
        self.assertEqual('DEBUG', entry.event_level)
        self.assertEqual('Module mode Change Requires Disconnect', entry.event)
        self.assertDictEqual({}, entry.conditions)

    def test_current_limited(self):
        entry = LogEntry('''
 07396     05/20/2018 16:15:31\
    Batt Dischg Cur Limited    281 A (40.72463768115942%), MinCell: 3383mV, MaxPackTemp: 34C''')
        self.assertEqual(7396, entry.entry)
        self.assertEqual('LIMIT', entry.event_type)
        self.assertEqual('Batt Dischg Cur Limited    281 A (40.72463768115942%),', entry.event)
        self.assertDictEqual({'MinCell': '3383mV',
                              'MaxPackTemp': '34C'},
                             entry.conditions)

    def test_error_entry(self):
        entry = LogEntry('''
 07758     05/20/2018 16:52:01\
   ERROR: Module 01 maximum connection retries reached. Flagging ineligble.    
''')
        self.assertEqual(7758, entry.entry)
        self.assertEqual('ERROR', entry.event_level)
        self.assertEqual('Battery', entry.component)
        self.assertEqual('Module 01 maximum connection retries reached. Flagging ineligble.',
                         entry.event)
        self.assertDictEqual({}, entry.conditions)
