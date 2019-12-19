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
usage: extract_ride_data.py [-h] [--format {csv,tsv,json}] [--verbose]
                            [--omit-units] [--outfile OUTFILE]
                            logfile

positional arguments:
  logfile               the parsed log file to process

optional arguments:
  -h, --help            show this help message and exit
  --format {csv,tsv,json}
                        the output format desired
  --verbose, -v         show more processing details
  --omit-units          omit units from the data values
  --outfile OUTFILE     the name of output file to emit
```

## Example
Run (say) `./extract_ride_data.py --format csv --outfile output.csv ~/Zero/Data/logs/my_logfile.txt`

Yields output like:
```csv
entry,timestamp,component,event_type,event_level,event,vmod,maxsys,minsys,diff,vcap,prechg,PackTemp (h),PackTemp (l),PackSOC,Vpack,MotAmps,BattAmps,Mods,MotTemp,CtrlTemp,AmbTemp,MotRPM,Odo,MinCell,MaxPackTemp,MbbChgEn,BmsChgEn,batt curr,Reset,serial,ImpedanceKOhms,Cell,Code,Error Reg,Error Code,Data,Bmvolts,Cmvolts,Amps,RPM,CapV
1,2018-05-13 10:06:43,Controller,,DEBUG,Sevcon Contactor Drive ON.,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
2,2018-05-13 10:06:43,Battery,,,Module 00 Closing Contactor,93.175,93.197,93.197,0.000,86.750,93%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
3,2018-05-13 10:06:43,Battery,,,Module 00 Closing Contactor,93.175,93.197,93.197,0.000,86.750,93%,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
4,2018-05-13 10:06:43,Battery,,DEBUG,Module 00 Contactor is now Closed,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
5,2018-05-13 10:06:43,External Charger,,INFO,Enabling External Chg 0 Charger 2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
6,2018-05-13 10:10:25,External Charger,DISCONNECTED,,External Chg 0 Charger 2 Disconnected,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
7,2018-05-13 10:10:25,Battery,,DEBUG,Module scheme changed from Charging mode to Stopped mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
8,2018-05-13 10:10:25,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
9,2018-05-13 10:10:32,Battery,,DEBUG,Module scheme changed from Stopped mode to Running mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
10,2018-05-13 10:10:32,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
11,2018-05-13 10:10:35,MBB,RIDING,,Riding,,,,,,,37,36,9%,93.271,108,1,10,43,23,18,0,46213km,,,,,,,,,,,,,,,,,,
12,2018-05-13 10:10:35,MBB,LIMIT,,Batt Dischg Cur Limited,,,,,,,,,15.217391304347826%,,,105,,,,,,,3.28,37,,,,,,,,,,,,,,,,
13,2018-05-13 10:10:42,Battery,,DEBUG,Module scheme changed from Running mode to Stopped mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
14,2018-05-13 10:10:42,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
15,2018-05-13 10:11:04,External Charger,CONNECTED,,External Chg 0 Charger 2 Connected,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
16,2018-05-13 10:11:04,Battery,,DEBUG,Module scheme changed from Stopped mode to Charging mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
17,2018-05-13 10:11:04,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
18,2018-05-13 10:11:04,External Charger,,INFO,Disabling External Chg 0 Charger 2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
19,2018-05-13 10:11:05,External Charger,,INFO,Enabling External Chg 0 Charger 2,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
20,2018-05-13 10:11:15,MBB,CHARGING,,Charging,,,,,,,37,36,9%,94.750,,-63,01,,,18,,,,,Yes,No,,,,,,,,,,,,,,
21,2018-05-13 10:11:55,MBB,OFF,,Key Off,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
22,2018-05-13 10:21:15,MBB,CHARGING,,Charging,,,,,,,37,36,21%,101.313,,-86,01,,,19,,,,,Yes,No,,,,,,,,,,,,,,
23,2018-05-13 10:31:15,MBB,CHARGING,,Charging,,,,,,,38,37,32%,103.378,,-86,01,,,20,,,,,Yes,No,,,,,,,,,,,,,,
24,2018-05-13 10:41:15,MBB,CHARGING,,Charging,,,,,,,39,38,44%,104.692,,-83,01,,,20,,,,,Yes,No,,,,,,,,,,,,,,
25,2018-05-13 10:51:15,MBB,CHARGING,,Charging,,,,,,,42,40,55%,107.101,,-82,01,,,21,,,,,Yes,No,,,,,,,,,,,,,,
26,2018-05-13 11:01:15,MBB,CHARGING,,Charging,,,,,,,44,43,66%,110.499,,-78,01,,,22,,,,,Yes,No,,,,,,,,,,,,,,
27,2018-05-13 11:09:02,MBB,ON,,Key On,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
28,2018-05-13 11:11:15,MBB,CHARGING,,Charging,,,,,,,45,45,77%,114.291,,-75,01,,,22,,,,,Yes,No,,,,,,,,,,,,,,
29,2018-05-13 11:15:05,External Charger,DISCONNECTED,,External Chg 0 Charger 2 Disconnected,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
30,2018-05-13 11:15:05,Battery,,DEBUG,Module scheme changed from Charging mode to Stopped mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
31,2018-05-13 11:15:05,Battery,,DEBUG,Module mode Change Does Not Require Disconnect,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
32,2018-05-13 11:15:15,MBB,,,Disarmed,,,,,,,45,45,80%,114.333,0,0,01,29,20,22,0,46213km,,,,,,,,,,,,,,,,,,
33,2018-05-13 11:15:15,Battery,,DEBUG,Module scheme changed from Stopped mode to Running mode,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
```
