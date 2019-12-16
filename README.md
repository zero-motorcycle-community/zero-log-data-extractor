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
usage: extract_ride_data.py [-h] [--format FORMAT] [--outfile OUTFILE] logfile

positional arguments:
  logfile            the parsed log file to process

optional arguments:
  -h, --help         show this help message and exit
  --format FORMAT    the output format desired: csv,tsv,json
  --outfile OUTFILE  the name of output file to emit
```

## Example
Run (say) `./extract_ride_data.py --format csv --outfile output.csv ~/Zero/Data/logs/my_logfile.txt`

Yields output like:
```csv
entry,timestamp,component,event_type,event,PackTemp (h),PackTemp (l),Vpack,BattAmps,MotTemp,AmbTemp,vmod,minsys,vcap,MinCell,PackSOC,MbbChgEn,serial,Error Code,Bmvolts,Amps
1,2018-05-21 21:12:20,MBB,,Disarmed,21,20,113.044,2,26,20,,,,,,,,,,
2,2018-05-13 10:06:37,Controller,,Sevcon CAN Link Down,,,,,,,,,,,,,,,,
3,2018-05-13 10:06:38,Controller,,Sevcon CAN Link Up,,,,,,,,,,,,,,,,
4,2018-05-13 10:06:40,MBB,,Contactor Welded,,,,,,,,,,,,,,,,
5,2018-05-13 10:06:40,Controller,OFF,Sevcon Turned Off,,,,,,,,,,,,,,,,
6,2018-05-13 10:06:42,Controller,ON,Sevcon Turned On,,,,,,,,,,,,,,,,
7,2018-05-13 10:06:42,Controller,,Sevcon CAN Link Down,,,,,,,,,,,,,,,,
8,2018-05-13 10:06:43,Controller,,Sevcon CAN Link Up,,,,,,,,,,,,,,,,
9,2018-05-13 10:06:43,Controller,DEBUG,Sevcon Contactor Drive ON.,,,,,,,,,,,,,,,,
10,2018-05-13 10:06:43,BMS,,Module 00,,,,,,,93.175,93.197,86.75,,,,,,,
11,2018-05-13 10:06:43,BMS,DEBUG,Module 00 Contactor is now Closed,,,,,,,,,,,,,,,,
12,2018-05-13 10:06:43,MBB,INFO, Enabling External Chg 0 Charger 2,,,,,,,,,,,,,,,,
13,2018-05-13 10:10:25,MBB,DISCONNECTED,External Chg 0 Charger 2 Disconnected,,,,,,,,,,,,,,,,
14,2018-05-13 10:10:25,BMS,DEBUG,Module scheme changed from Charging mode to Stopped mode,,,,,,,,,,,,,,,,
15,2018-05-13 10:10:25,BMS,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,
16,2018-05-13 10:10:32,BMS,DEBUG,Module scheme changed from Stopped mode to Running mode,,,,,,,,,,,,,,,,
17,2018-05-13 10:10:32,BMS,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,
18,2018-05-13 10:10:35,MBB,RIDING,Riding,37,36,93.271,1,43,18,,,,,,,,,,
19,2018-05-13 10:10:35,MBB,,Batt Dischg Cur Limited,,,,,,,,,,3.28,,,,,,
20,2018-05-13 10:10:42,BMS,DEBUG,Module scheme changed from Running mode to Stopped mode,,,,,,,,,,,,,,,,
21,2018-05-13 10:10:42,BMS,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,
22,2018-05-13 10:11:04,MBB,CONNECTED,External Chg 0 Charger 2 Connected,,,,,,,,,,,,,,,,
23,2018-05-13 10:11:04,BMS,DEBUG,Module scheme changed from Stopped mode to Charging mode,,,,,,,,,,,,,,,,
24,2018-05-13 10:11:04,BMS,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,
25,2018-05-13 10:11:04,MBB,INFO, Disabling External Chg 0 Charger 2,,,,,,,,,,,,,,,,
26,2018-05-13 10:11:05,MBB,INFO, Enabling External Chg 0 Charger 2,,,,,,,,,,,,,,,,
27,2018-05-13 10:11:15,MBB,CHARGING,Charging,37,36,,-63,,,,,,,9%,Yes,,,,
28,2018-05-13 10:11:55,MBB,OFF,Key Off,,,,,,,,,,,,,,,,
29,2018-05-13 10:21:15,MBB,CHARGING,Charging,37,36,,-86,,,,,,,21%,Yes,,,,
30,2018-05-13 10:31:15,MBB,CHARGING,Charging,38,37,,-86,,,,,,,32%,Yes,,,,
31,2018-05-13 10:41:15,MBB,CHARGING,Charging,39,38,,-83,,,,,,,44%,Yes,,,,
32,2018-05-13 10:51:15,MBB,CHARGING,Charging,42,40,,-82,,,,,,,55%,Yes,,,,
33,2018-05-13 11:01:15,MBB,CHARGING,Charging,44,43,,-78,,,,,,,66%,Yes,,,,
```
