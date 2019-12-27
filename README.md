# Log Extractor for Zero Motorcycles models
Turn decoded (text) Zero log file contents into various usable data formats

## Homepage
* https://github.com/zero-motorcycle-community/zero-log-data-extractor

## Installation
Run `git clone https://github.com/zero-motorcycle-community/zero-log-data-extractor`

## Requirements
* Install python 3 to run this script.
* Only python 3 standard libraries are required, so there is no additional requirement.

## Usage
Run the script from a command line or other script management tool.

```
usage: extract_ride_data.py [-h] [--format {csv,tsv,json,all}] [--verbose]
                            [--omit-units] [--outfile OUTFILE]
                            logfile

positional arguments:
  logfile               the parsed log file to process

optional arguments:
  -h, --help            show this help message and exit
  --format {csv,tsv,json,all}
                        the output format desired
  --verbose, -v         show more processing details
  --omit-units          omit units from the data values
  --outfile OUTFILE     the name of output file to emit
```

## Example
Run (say) `./extract_ride_data.py --format csv --outfile output.csv ~/Zero/Data/logs/my_logfile.txt`

Yields output like:
```csv
entry,segment_id,segment_activity,timestamp,component,event_type,event_level,event,vmod,maxsys,minsys,diff,vcap,prechg,Module,PackTemp (h),PackTemp (l),PackSOC,Vpack,MotAmps,BattAmps,Mods,MotTemp,CtrlTemp,AmbTemp,MotRPM,Odo,MinCell,MaxPackTemp,MbbChgEn,BmsChgEn,batt curr,Reset,serial,ImpedanceKOhms,Cell,PV,Allowed diff,pack cap,PackTemp h,l,lcell,Max charge,max discharge,Code,Error Reg,Error Code,Data,Bmvolts,Cmvolts,Amps,RPM,CapV
1,0,STOPPED,2018-05-13 10:06:43,Controller,,DEBUG,Sevcon Contactor Drive ON.,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2,1,STARTED,2018-05-13 10:06:43,Battery,,,Module Closing Contactor,93.175,93.197,93.197,0.000,86.750,93%,00,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
3,2,STARTED,2018-05-13 10:06:43,Battery,,,Module Closing Contactor,93.175,93.197,93.197,0.000,86.750,93%,00,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
4,2,STARTED,2018-05-13 10:06:43,Battery,,DEBUG,Module Contactor is now Closed,,,,,,,00,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
5,2,STARTED,2018-05-13 10:06:43,External Charger,ENABLING,INFO,Enabling External Chg 0 Charger 2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
6,2,STARTED,2018-05-13 10:10:25,External Charger,DISCONNECTED,,External Chg 0 Charger 2 Disconnected,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
7,2,STARTED,2018-05-13 10:10:25,Battery,,DEBUG,Module scheme changed from Charging mode to Stopped mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
8,2,STARTED,2018-05-13 10:10:25,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
9,2,STARTED,2018-05-13 10:10:32,Battery,,DEBUG,Module scheme changed from Stopped mode to Running mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
10,2,STARTED,2018-05-13 10:10:32,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
11,3,RIDING,2018-05-13 10:10:35,MBB,RIDING,,Riding,,,,,,,,37,36,9%,93.271,108,1,10,43,23,18,0,46213km,,,,,,,,,,,,,,,,,,,,,,,,,,
12,3,RIDING,2018-05-13 10:10:35,MBB,LIMIT,,Batt Dischg Cur Limited,,,,,,,,,,15.217391304347826%,,,105,,,,,,,3.28,37,,,,,,,,,,,,,,,,,,,,,,,,
13,3,RIDING,2018-05-13 10:10:42,Battery,,DEBUG,Module scheme changed from Running mode to Stopped mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
14,3,RIDING,2018-05-13 10:10:42,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
15,3,RIDING,2018-05-13 10:11:04,External Charger,CONNECTED,,External Chg 0 Charger 2 Connected,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
16,4,CHARGING,2018-05-13 10:11:04,Battery,CHARGING,DEBUG,Module scheme changed from Stopped mode to Charging mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
17,4,CHARGING,2018-05-13 10:11:04,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
18,4,CHARGING,2018-05-13 10:11:04,External Charger,DISABLING,INFO,Disabling External Chg 0 Charger 2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
19,4,CHARGING,2018-05-13 10:11:05,External Charger,ENABLING,INFO,Enabling External Chg 0 Charger 2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
20,4,CHARGING,2018-05-13 10:11:15,MBB,CHARGING,,Charging,,,,,,,,37,36,9%,94.750,,-63,01,,,18,,,,,Yes,No,,,,,,,,,,,,,,,,,,,,,,
21,4,CHARGING,2018-05-13 10:11:55,MBB,OFF,,Key Off,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
22,4,CHARGING,2018-05-13 10:21:15,MBB,CHARGING,,Charging,,,,,,,,37,36,21%,101.313,,-86,01,,,19,,,,,Yes,No,,,,,,,,,,,,,,,,,,,,,,
23,4,CHARGING,2018-05-13 10:31:15,MBB,CHARGING,,Charging,,,,,,,,38,37,32%,103.378,,-86,01,,,20,,,,,Yes,No,,,,,,,,,,,,,,,,,,,,,,
24,4,CHARGING,2018-05-13 10:41:15,MBB,CHARGING,,Charging,,,,,,,,39,38,44%,104.692,,-83,01,,,20,,,,,Yes,No,,,,,,,,,,,,,,,,,,,,,,
25,4,CHARGING,2018-05-13 10:51:15,MBB,CHARGING,,Charging,,,,,,,,42,40,55%,107.101,,-82,01,,,21,,,,,Yes,No,,,,,,,,,,,,,,,,,,,,,,
26,4,CHARGING,2018-05-13 11:01:15,MBB,CHARGING,,Charging,,,,,,,,44,43,66%,110.499,,-78,01,,,22,,,,,Yes,No,,,,,,,,,,,,,,,,,,,,,,
27,4,CHARGING,2018-05-13 11:09:02,MBB,ON,,Key On,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
28,4,CHARGING,2018-05-13 11:11:15,MBB,CHARGING,,Charging,,,,,,,,45,45,77%,114.291,,-75,01,,,22,,,,,Yes,No,,,,,,,,,,,,,,,,,,,,,,
29,4,CHARGING,2018-05-13 11:15:05,External Charger,DISCONNECTED,,External Chg 0 Charger 2 Disconnected,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
30,4,CHARGING,2018-05-13 11:15:05,Battery,,DEBUG,Module scheme changed from Charging mode to Stopped mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
31,4,CHARGING,2018-05-13 11:15:05,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
32,4,CHARGING,2018-05-13 11:15:15,MBB,,,Disarmed,,,,,,,,45,45,80%,114.333,0,0,01,29,20,22,0,46213km,,,,,,,,,,,,,,,,,,,,,,,,,,
33,4,CHARGING,2018-05-13 11:15:15,Battery,,DEBUG,Module scheme changed from Stopped mode to Running mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
```

And in JSON:
```json
{
  "header": {
    "source": "MBB",
    "title": "﻿Zero MBB log",
    "metadata": {
      "serial_no": "2015_mbb_48e0f7_00720",
      "vin": "538SD9Z37GCGxxxxx",
      "firmware_rev": "51",
      "board_rev": "3",
      "model": "DSR",
      "num_entries": 8397,
      "num_entries_expected": 8397
    }
  },
  "entries": [
    {
      "entry": 1,
      "segment_id": 0,
      "segment_activity": "STOPPED",
      "timestamp": "2018-05-13 10:06:43",
      "component": "Controller",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Sevcon Contactor Drive ON.",
      "conditions": {}
    },
    {
      "entry": 2,
      "segment_id": 1,
      "segment_activity": "STARTED",
      "timestamp": "2018-05-13 10:06:43",
      "component": "Battery",
      "event_type": "",
      "event_level": "",
      "event": "Module Closing Contactor",
      "conditions": {
        "vmod": "93.175V",
        "maxsys": "93.197V",
        "minsys": "93.197V",
        "diff": "0.000V",
        "vcap": "86.750V",
        "prechg": "93%",
        "Module": "00"
      }
    },
    {
      "entry": 3,
      "segment_id": 2,
      "segment_activity": "STARTED",
      "timestamp": "2018-05-13 10:06:43",
      "component": "Battery",
      "event_type": "",
      "event_level": "",
      "event": "Module Closing Contactor",
      "conditions": {
        "vmod": "93.175V",
        "maxsys": "93.197V",
        "minsys": "93.197V",
        "diff": "0.000V",
        "vcap": "86.750V",
        "prechg": "93%",
        "Module": "00"
      }
    },
    {
      "entry": 4,
      "segment_id": 2,
      "segment_activity": "STARTED",
      "timestamp": "2018-05-13 10:06:43",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module Contactor is now Closed",
      "conditions": {
        "Module": "00"
      }
    },
    {
      "entry": 5,
      "segment_id": 2,
      "segment_activity": "STARTED",
      "timestamp": "2018-05-13 10:06:43",
      "component": "External Charger",
      "event_type": "ENABLING",
      "event_level": "INFO",
      "event": "Enabling External Chg 0 Charger 2",
      "conditions": {}
    },
    {
      "entry": 6,
      "segment_id": 2,
      "segment_activity": "STARTED",
      "timestamp": "2018-05-13 10:10:25",
      "component": "External Charger",
      "event_type": "DISCONNECTED",
      "event_level": "",
      "event": "External Chg 0 Charger 2 Disconnected",
      "conditions": {}
    },
    {
      "entry": 7,
      "segment_id": 2,
      "segment_activity": "STARTED",
      "timestamp": "2018-05-13 10:10:25",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module scheme changed from Charging mode to Stopped mode",
      "conditions": {}
    },
    {
      "entry": 8,
      "segment_id": 2,
      "segment_activity": "STARTED",
      "timestamp": "2018-05-13 10:10:25",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module mode Change Does Not Require Disconnect",
      "conditions": {}
    },
    {
      "entry": 9,
      "segment_id": 2,
      "segment_activity": "STARTED",
      "timestamp": "2018-05-13 10:10:32",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module scheme changed from Stopped mode to Running mode",
      "conditions": {}
    },
    {
      "entry": 10,
      "segment_id": 2,
      "segment_activity": "STARTED",
      "timestamp": "2018-05-13 10:10:32",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module mode Change Does Not Require Disconnect",
      "conditions": {}
    },
    {
      "entry": 11,
      "segment_id": 3,
      "segment_activity": "RIDING",
      "timestamp": "2018-05-13 10:10:35",
      "component": "MBB",
      "event_type": "RIDING",
      "event_level": "",
      "event": "Riding",
      "conditions": {
        "PackTemp (h)": "37C",
        "PackTemp (l)": "36C",
        "PackSOC": "9%",
        "Vpack": "93.271V",
        "MotAmps": "108",
        "BattAmps": "1",
        "Mods": "10",
        "MotTemp": "43C",
        "CtrlTemp": "23C",
        "AmbTemp": "18C",
        "MotRPM": "0",
        "Odo": "46213km"
      }
    },
    {
      "entry": 12,
      "segment_id": 3,
      "segment_activity": "RIDING",
      "timestamp": "2018-05-13 10:10:35",
      "component": "MBB",
      "event_type": "LIMIT",
      "event_level": "",
      "event": "Batt Dischg Cur Limited",
      "conditions": {
        "MinCell": "3280mV",
        "MaxPackTemp": "37C",
        "BattAmps": "105",
        "PackSOC": "15.217391304347826%"
      }
    },
    {
      "entry": 13,
      "segment_id": 3,
      "segment_activity": "RIDING",
      "timestamp": "2018-05-13 10:10:42",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module scheme changed from Running mode to Stopped mode",
      "conditions": {}
    },
    {
      "entry": 14,
      "segment_id": 3,
      "segment_activity": "RIDING",
      "timestamp": "2018-05-13 10:10:42",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module mode Change Does Not Require Disconnect",
      "conditions": {}
    },
    {
      "entry": 15,
      "segment_id": 3,
      "segment_activity": "RIDING",
      "timestamp": "2018-05-13 10:11:04",
      "component": "External Charger",
      "event_type": "CONNECTED",
      "event_level": "",
      "event": "External Chg 0 Charger 2 Connected",
      "conditions": {}
    },
    {
      "entry": 16,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:11:04",
      "component": "Battery",
      "event_type": "CHARGING",
      "event_level": "DEBUG",
      "event": "Module scheme changed from Stopped mode to Charging mode",
      "conditions": {}
    },
    {
      "entry": 17,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:11:04",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module mode Change Does Not Require Disconnect",
      "conditions": {}
    },
    {
      "entry": 18,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:11:04",
      "component": "External Charger",
      "event_type": "DISABLING",
      "event_level": "INFO",
      "event": "Disabling External Chg 0 Charger 2",
      "conditions": {}
    },
    {
      "entry": 19,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:11:05",
      "component": "External Charger",
      "event_type": "ENABLING",
      "event_level": "INFO",
      "event": "Enabling External Chg 0 Charger 2",
      "conditions": {}
    },
    {
      "entry": 20,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:11:15",
      "component": "MBB",
      "event_type": "CHARGING",
      "event_level": "",
      "event": "Charging",
      "conditions": {
        "PackTemp (h)": "37C",
        "PackTemp (l)": "36C",
        "AmbTemp": "18C",
        "PackSOC": "9%",
        "Vpack": "94.750V",
        "BattAmps": "-63",
        "Mods": "01",
        "MbbChgEn": "Yes",
        "BmsChgEn": "No"
      }
    },
    {
      "entry": 21,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:11:55",
      "component": "MBB",
      "event_type": "OFF",
      "event_level": "",
      "event": "Key Off",
      "conditions": {}
    },
    {
      "entry": 22,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:21:15",
      "component": "MBB",
      "event_type": "CHARGING",
      "event_level": "",
      "event": "Charging",
      "conditions": {
        "PackTemp (h)": "37C",
        "PackTemp (l)": "36C",
        "AmbTemp": "19C",
        "PackSOC": "21%",
        "Vpack": "101.313V",
        "BattAmps": "-86",
        "Mods": "01",
        "MbbChgEn": "Yes",
        "BmsChgEn": "No"
      }
    },
    {
      "entry": 23,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:31:15",
      "component": "MBB",
      "event_type": "CHARGING",
      "event_level": "",
      "event": "Charging",
      "conditions": {
        "PackTemp (h)": "38C",
        "PackTemp (l)": "37C",
        "AmbTemp": "20C",
        "PackSOC": "32%",
        "Vpack": "103.378V",
        "BattAmps": "-86",
        "Mods": "01",
        "MbbChgEn": "Yes",
        "BmsChgEn": "No"
      }
    },
    {
      "entry": 24,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:41:15",
      "component": "MBB",
      "event_type": "CHARGING",
      "event_level": "",
      "event": "Charging",
      "conditions": {
        "PackTemp (h)": "39C",
        "PackTemp (l)": "38C",
        "AmbTemp": "20C",
        "PackSOC": "44%",
        "Vpack": "104.692V",
        "BattAmps": "-83",
        "Mods": "01",
        "MbbChgEn": "Yes",
        "BmsChgEn": "No"
      }
    },
    {
      "entry": 25,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 10:51:15",
      "component": "MBB",
      "event_type": "CHARGING",
      "event_level": "",
      "event": "Charging",
      "conditions": {
        "PackTemp (h)": "42C",
        "PackTemp (l)": "40C",
        "AmbTemp": "21C",
        "PackSOC": "55%",
        "Vpack": "107.101V",
        "BattAmps": "-82",
        "Mods": "01",
        "MbbChgEn": "Yes",
        "BmsChgEn": "No"
      }
    },
    {
      "entry": 26,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 11:01:15",
      "component": "MBB",
      "event_type": "CHARGING",
      "event_level": "",
      "event": "Charging",
      "conditions": {
        "PackTemp (h)": "44C",
        "PackTemp (l)": "43C",
        "AmbTemp": "22C",
        "PackSOC": "66%",
        "Vpack": "110.499V",
        "BattAmps": "-78",
        "Mods": "01",
        "MbbChgEn": "Yes",
        "BmsChgEn": "No"
      }
    },
    {
      "entry": 27,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 11:09:02",
      "component": "MBB",
      "event_type": "ON",
      "event_level": "",
      "event": "Key On",
      "conditions": {}
    },
    {
      "entry": 28,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 11:11:15",
      "component": "MBB",
      "event_type": "CHARGING",
      "event_level": "",
      "event": "Charging",
      "conditions": {
        "PackTemp (h)": "45C",
        "PackTemp (l)": "45C",
        "AmbTemp": "22C",
        "PackSOC": "77%",
        "Vpack": "114.291V",
        "BattAmps": "-75",
        "Mods": "01",
        "MbbChgEn": "Yes",
        "BmsChgEn": "No"
      }
    },
    {
      "entry": 29,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 11:15:05",
      "component": "External Charger",
      "event_type": "DISCONNECTED",
      "event_level": "",
      "event": "External Chg 0 Charger 2 Disconnected",
      "conditions": {}
    },
    {
      "entry": 30,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 11:15:05",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module scheme changed from Charging mode to Stopped mode",
      "conditions": {}
    },
    {
      "entry": 31,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 11:15:05",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module mode Change Does Not Require Disconnect",
      "conditions": {}
    },
    {
      "entry": 32,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 11:15:15",
      "component": "MBB",
      "event_type": "",
      "event_level": "",
      "event": "Disarmed",
      "conditions": {
        "PackTemp (h)": "45C",
        "PackTemp (l)": "45C",
        "PackSOC": "80%",
        "Vpack": "114.333V",
        "MotAmps": "0",
        "BattAmps": "0",
        "Mods": "01",
        "MotTemp": "29C",
        "CtrlTemp": "20C",
        "AmbTemp": "22C",
        "MotRPM": "0",
        "Odo": "46213km"
      }
    },
    {
      "entry": 33,
      "segment_id": 4,
      "segment_activity": "CHARGING",
      "timestamp": "2018-05-13 11:15:15",
      "component": "Battery",
      "event_type": "",
      "event_level": "DEBUG",
      "event": "Module scheme changed from Stopped mode to Running mode",
      "conditions": {}
    }
  ]
}
```

## Example Scripts

Select all riding events from JSON:
```shell script
jq '.entries|map(select(.event_type=="RIDING"))' example.json
```
