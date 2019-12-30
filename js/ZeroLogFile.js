"use strict";

const EMPTY_CSV_VALUE = '';
const COMMA = ',';
const TAB = '\t';

/**
 * @param value
 * @param omitUnits {Boolean}
 * @returns {string}
 */
function printValueTabular(value, omitUnits=false) {
  if (value === undefined || value === null) {
    return EMPTY_CSV_VALUE;
  }
  if (omitUnits && typeof value === 'string') {
    const match = value.match(/^([0-9.]+)\s*([A-Za-z]+)$/);
    if (match) {
      return match[0];
    }
  }
  return value.toString();
}

/**
 * @property {string} logTitle
 * @property {[string]} columnLabels
 */
class LogHeader {
  constructor() {
  }
}

/**
 * @property {?Date} timestamp
 * @property {?string} logTag
 * @property {[string]} fieldValues
 * @property {Object.<string, string|number>} conditions
 */
class LogEntry {
  constructor(logText, index=null, fieldSep=undefined) {
    if (fieldSep) {
      this.fieldValues = logText.split(fieldSep).map((fieldValue) => fieldValue.trim());
    }
    this.conditions = {};
  }

  /**
   * @param timestampText {string}
   * @returns {?Date}
   */
  decodeTimestamp(timestampText) {
    try {
      return new Date(Date.parse(timestampText));
    } catch (e) {
      return null;
    }
  }

  printPropertyTabular(index, key, omitUnits=false) {
    if (this.hasOwnProperty(key)) {
      return printValueTabular(this[key], omitUnits);
    }
    if (this.fieldValues) {
      return printValueTabular(this.fieldValues[index], omitUnits);
    }
    return EMPTY_CSV_VALUE;
  }

  toRowValues(headers, omitUnits=false) {
    return headers.map(
      (header, index) => this.printPropertyTabular(index, header, omitUnits)
    );
  }

  toCSV(headers, fieldSep=COMMA, omitUnits=false) {
    return this.toRowValues(headers, omitUnits).join(fieldSep);
  }

  toTSV(headers, omitUnits=false) {
    return this.toCSV(headers, TAB, omitUnits);
  }

  toJSON() {
    return {
      timestamp: this.timestamp ? this.timestamp.toISOString() : ''
    };
  }
}

/** Allows timestamp-based sorting of entries.
 * @param logEntry {LogEntry}
 * @param other {LogEntry}
 * @returns {number}
 */
function LogEntryCompare (logEntry, other) {
  const thisTimestamp = logEntry.timestamp,
    otherTimestamp = other.timestamp;
  if (thisTimestamp > otherTimestamp) {
    return 1;
  } else if (thisTimestamp < otherTimestamp) {
    return -1;
  }
  return 0;
}

/**
 * @property {[LogEntry]} entries
 * @property {[string]} tabularHeaderLabels
 */
class LogData {
  /**
   * @param entries {[LogEntry]}
   * @param tabularHeaderLabels {[string]}
   */
  constructor(entries, tabularHeaderLabels) {
    this.entries = entries;
    this.tabularHeaderLabels = tabularHeaderLabels || [];
  }

  refresh() {}

  toTabularLines(fieldSep=COMMA, omitUnits=false) {
    const headers = this.tabularHeaderLabels;
    return this.entries.map(
      (logEntry) => logEntry.toCSV(headers, fieldSep, omitUnits)
    );
  }

  toJSON() {
    return {
      entries: this.entries.map((logEntry) => logEntry.toJSON())
    };
  }

  toFormat(outputFormat, omitUnits=false) {
    switch (outputFormat) {
      case 'csv':
        return this.toTabularLines(COMMA, omitUnits);
      case 'tsv':
        return this.toTabularLines(TAB, omitUnits);
      case 'json':
        return this.toJSON();
    }
  }
}

class ZeroMBBHeaderMetadata {
  constructor(serialNo, vin, firmwareRev, boardRev, model) {
    this.serialNo = serialNo;
    this.vin = vin;
    this.firmwareRev = firmwareRev;
    this.boardRev = boardRev;
    this.model = model;
  }

  toJSON() {
    return {
      serial_no: this.serialNo,
      vin: this.vin,
      firmware_rev: this.firmwareRev,
      board_rev: this.boardRev,
      model: this.model
    };
  }
}

class ZeroBMSHeaderMetadata {
  constructor(serialNo, packSerialNo, initialDate) {
    this.serialNo = serialNo;
    this.packSerialNo = packSerialNo;
    this.initialDate = new Date(Date.parse(initialDate));
  }

  toJSON() {
    return {
      serial_no: this.serialNo,
      pack_serial_no: this.packSerialNo,
      initial_date: this.initialDate.toISOString()
    };
  }}

/**
 * @param logLine {string}
 * @return {boolean}
 */
function isLogDividerLine(logLine) {
  return logLine.startsWith('+-----');
}

/**
 * @property {string} logTitle
 * @property {ZeroMBBHeaderMetadata|ZeroBMSHeaderMetadata|null} metadata
 * @property {number} logCountActual
 * @property {number} logCountExpected
 * @property {[number]|Uint8Array} dividerIndexes
 */
class ZeroLogHeader extends LogHeader {
  constructor(logLines) {
    super();
    console.debug('Reading header');
    const headerLines = logLines.slice(0, this.indexOfDividerLine(logLines) + 1);
    this.logTitle = headerLines[0].trim();
    switch (this.logSource) {
      case 'MBB':
        this.metadata = new ZeroMBBHeaderMetadata(
          this.valueFromHeaderLines(headerLines, 'Serial number'),
          this.valueFromHeaderLines(headerLines, 'VIN'),
          this.valueFromHeaderLines(headerLines, 'Firmware rev.'),
          this.valueFromHeaderLines(headerLines, 'Board rev.'),
          this.valueFromHeaderLines(headerLines, 'Model')
        );
        break;
      case 'BMS':
        this.metadata = new ZeroBMSHeaderMetadata(
          this.valueFromHeaderLines(headerLines, 'BMS serial number'),
          this.valueFromHeaderLines(headerLines, 'Pack serial number'),
          this.valueFromHeaderLines(headerLines, 'Initial date')
        );
        break;
    }
    const lastFourLines = headerLines.slice(-4);
    const logCountMatches = lastFourLines[0].matchAll(/\d+/).map(Number.parseInt);
    this.logCountActual = logCountMatches[0];
    this.logCountExpected = logCountMatches[1];
    this.dividerIndexes = lastFourLines[2].map(
      (char, index) => char === '+' ? index : undefined
    ).filter(
      (maybeIndex) => Number.isInteger(maybeIndex)
    );
    this.columnLabels = lastFourLines[3].split(/\s\s+/).map((x) => x.trim());
  }

  get logSource() {
    if (this.logTitle.includes('MBB')) {
      return 'MBB';
    }
    if (this.logTitle.includes('BMS')) {
      return 'BMS';
    }
  }

  /**
   * @param logLines {[string]}
   * @returns {number}
   */
  indexOfDividerLine(logLines) {
    let lastHeaderLineIndex = 0;
    while (!isLogDividerLine(logLines[lastHeaderLineIndex])) {
      lastHeaderLineIndex++;
    }
    return lastHeaderLineIndex;
  }

  /**
   * @param headerLine {string}
   * @param prefix {?string}
   * @returns {string}
   */
  valueFromHeaderLine(headerLine, prefix=undefined) {
    if (prefix) {
      return headerLine.slice(0-prefix.length).trim();
    }
    const labelAndValue = headerLine.trim().split(/\s\s+/);
    return labelAndValue[1];
  }

  /**
   * @param headerLines {[string]}
   * @param prefix {?string}
   */
  valueFromHeaderLines(headerLines, prefix) {
    const matchingLine = headerLines.find((headerLine) => headerLine.startsWith(prefix));
    if (matchingLine) {
      return this.valueFromHeaderLine(matchingLine, prefix);
    }
  }

  toJSON() {
    return {
      source: this.logSource,
      title: this.logTitle,
      metadata: this.metadata ? this.metadata.toJSON() : undefined,
      num_entries: this.logCountActual,
      num_entries_expected: this.logCountExpected
    };
  }
}

class ZeroLogEntry extends LogEntry {
  /** @type {number} */
  entry = 0;
  /** @type {number} */
  segmentID = 0;
  /** @type {string} */
  segmentActivity = EMPTY_CSV_VALUE;
  /** @type {string} */
  eventLevel = EMPTY_CSV_VALUE;
  /** @type {string} */
  eventType = EMPTY_CSV_VALUE;
  /** @type {string} */
  event = EMPTY_CSV_VALUE;
  /** @type {string} */
  component = EMPTY_CSV_VALUE;

  constructor(logLine, index) {
    super(logLine, index);
    try {
      this.entry = Number.parseInt(logLine.slice(0, 9).trim());
      const timestampText = logLine.slice(10, 32).trim();
      if (timestampText) {
        try {
          this.timestamp = this.decodeTimestamp(timestampText);
        } catch (e) {
          console.warn("Unable to parse timestamp", timestampText);
        }
      }
    } catch (e) {
      console.error("Decoding line failed from content: ", index, logLine);
    }
  }

  /** Extract and strip log level, return level and remainder
   * @param messageText {string}
   * @return {(string|string)[]}
   */
  levelAndMessageFrom(messageText) {
    let eventLevel = EMPTY_CSV_VALUE;
    let eventContents = messageText;
    if (eventContents.startsWith('INFO:')) {
      eventLevel = 'INFO';
      eventContents = eventContents.slice(6).trim();
    } else if (eventContents.startsWith('DEBUG:')) {
      eventLevel = 'DEBUG';
      eventContents = eventContents.slice(7).trim();
    } else if (eventContents.startsWith('- DEBUG:')) {
      eventLevel = 'DEBUG';
      eventContents = eventContents.slice(9).trim();
    } else if (eventContents.startsWith('WARNING:')) {
      eventLevel = 'WARNING';
      eventContents = eventContents.slice(8).trim();
    } else if (eventContents.startsWith('ERROR:')) {
      eventLevel = 'ERROR';
      eventContents = eventContents.slice(7).trim();
    } else if (eventContents.includes(' error')) {
      eventLevel = 'ERROR';
    }
    return [eventLevel, eventContents];
  }

  eventTypesByPrefix = {
    '0x': 'UNKNOWN',
    'Riding': 'RIDING',
    'Charging': 'CHARGING',
    'Enabling': 'ENABLING',
    'Disabling': 'DISABLING'
  };

  eventTypesBySuffix = {
    ' Connected': 'CONNECTED',
    ' Disconnected': 'DISCONNECTED',
    ' Link Up': 'CONNECTED',
    ' Link Down': 'DISCONNECTED',
    ' On': 'ON',
    ' Off': 'OFF'
  };

  /** Check contents for event type.
   * @param messageText {string}
   * @return {string}
   */
  decodeTypeFromMessage(messageText) {
    let eventType = EMPTY_CSV_VALUE;
    for (let [prefix, eventTypeValue] of this.eventTypesByPrefix) {
      if (messageText.startsWith(prefix)) {
        eventType = eventTypeValue;
        break;
      }
    }
    for (let [suffix, eventTypeValue] of this.eventTypesBySuffix) {
      if (messageText.endsWith(suffix)) {
        eventType = eventTypeValue;
        break;
      }
    }
    if (messageText.startsWith('Turning')) {
      if (messageText.includes('ON')) {
        eventType = 'ON';
      } else if (messageText.includes('OFF')) {
        eventType = 'OFF';
      }
    }
    if (messageText.includes('Charging') &&
      !messageText.includes('from Charging')) {
      eventType = 'CHARGING';
    }
    if (messageText.includes('LIMIT')) {
      eventType = 'LIMIT';
    }
    return eventType;
  }

  componentsByMessagePart = {
    'Battery': 'Battery',
    'Sevcon': 'Controller',
    'DCDC': 'DC-DC Converter',
    'Calex': 'Charger',
    'External Chg': 'External Charger',
    'Charger 6': 'Charge Tank'
  };

  /** Check contents for components
   * @param messageText {string}
   * @return {string}
   */
  decodeComponentFromMessage(messageText) {
    let component = 'MBB';
    if (messageText.startsWith('Module ')) {
      component = 'Battery';
    } else {
      for (let [part, componentValue] of this.componentsByMessagePart) {
        if (messageText.includes(part)) {
          component = componentValue;
          break;
        }
      }
    }
    return component;
  }

  currentLimitedMessage = 'Batt Dischg Cur Limited';
  lowChassisIsolationMessage = 'Low Chassis Isolation';
  moduleNoConditionKey = 'Module';

  /** Identify special conditions in the event contents
   * @param messageText {string}
   * @return {string}
   */
  decodeSpecialMessageConditions(messageText) {
    if (messageText.startsWith(this.currentLimitedMessage)) {
      // TODO decode per decode_special_message_conditions
      return this.currentLimitedMessage;
    }
    if (messageText.startsWith(this.lowChassisIsolationMessage)) {
      // TODO decode per decode_special_message_conditions
      return this.lowChassisIsolationMessage;
    }
    // TODO finish per decode_special_message_conditions
    return messageText;
  }

  /** Extract LogEntry properties from the log text after the timestamp.
   * @param messageText {string}
   */
  decodeMessage(messageText) {
    let [level, eventContents] = this.levelAndMessageFrom(messageText);
    this.eventLevel = level;
    this.eventType = this.decodeTypeFromMessage(eventContents);
    if (this.eventType === 'UNKNOWN') {
      eventContents = EMPTY_CSV_VALUE;
    }

    this.component = this.decodeComponentFromMessage(eventContents);

    const firstKeywordMatch = /[A-Za-z]+:/.exec(eventContents);
    if (firstKeywordMatch) {
      const idx = firstKeywordMatch.index;
      const conditionsField = eventContents.slice(idx).trim();
      eventContents = eventContents.slice(0, idx).trim();
      this.conditions = this.decodeConditionsText(conditionsField);
    } else {
      this.conditions = {};
    }

    eventContents = this.decodeSpecialMessageConditions(eventContents);

    this.event = eventContents;
  }

  /** Extract key-value data pairs in the message and conditions text.
   * @param conditionsText {string}
   * @return {Object.<string, string>}
   */
  decodeConditionsText(conditionsText) {
    const result = {};
    /** @type {[RegExpExecArray]} */
    const keyMatches = [];
    const keyMatcher = /,?\s*([A-Za-z]+\s*[A-Za-z]*):\s*/g.compile();
    let keyMatch;
    while ((keyMatch = keyMatcher.exec(conditionsText))) {
      keyMatches.push(keyMatch);
    }
    const lastIndex = keyMatches.length - 1;
    keyMatches.forEach((keyMatch, index) => {
      const key = keyMatch[1];
      if (index < lastIndex) {
        const nextMatch = keyMatches[index + 1];
        const value = conditionsText.slice(keyMatch.index, nextMatch.index);
        if (value.includes(COMMA)) {
          value.split(/,s*/).forEach((eachValue) => {
            if (eachValue.includes(' ')) {
              let [eachKey, eachVal] = eachValue.split(/\s+/);
              result[key + ' (' + eachKey + ')'] = eachVal;
            } else {
              result[key] = value;
            }
          });
        } else {
          result[key] = value;
        }
      } else { // Get the last key-value pair:
        result[key] = conditionsText.slice(keyMatch.index);
      }
    });
    return result;
  }

  /** Whether the event has a log level.
   * @returns {Boolean}
   */
  hasLogLevel() {
    return ['INFO', 'DEBUG', 'WARNING', 'ERROR'].includes(this.eventLevel);
  }

  /** Whether the event is battery-related.
   * @returns {Boolean}
   */
  isBatteryEvent() {
    return this.component === 'Battery';
  }

  /** Which battery module, if any, is involved.
   * @returns {?number}
   */
  get batteryModuleNo() {
    if (this.isBatteryEvent()) {
      return Number.parseInt(this.conditions[this.moduleNoConditionKey]);
    }
    return null;
  }

  /** Whether the event means the/a contactor is closing.
   * @returns {Boolean}
   */
  isContactorCloseEntry() {
    return (this.isBatteryEvent() &&
      this.event === 'Module Closing Contactor' &&
      this.batteryModuleNo === 0);
  }

  /** Whether the event means the/a contactor is closing.
   * @return {Boolean}
   */
  isContactorOpenEntry() {
    return (this.isBatteryEvent() &&
      this.event === 'Module Opening Contactor' &&
      this.batteryModuleNo === 0);
  }

  /** Whether the event means the/a contactor is closing.
   * @return {Boolean}
   */
  isRunningEntry() {
    return this.eventType === 'RIDING';
  }

  /** Whether the event is a charging event.
   * @return {Boolean}
   */
  isChargingEntry() {
    return this.eventType === 'CHARGING';
  }

  /** For tabular output, print a built-in property or condition value.
   * @return {string}
   */
  printPropertyTabular(index, key, omitUnits = false) {
    if (this.hasOwnProperty(key)) {
      return printValueTabular(this[key], omitUnits);
    }
    if (this.conditions.hasOwnProperty(key)) {
      const value = this.conditions[key];
      if (/^d*.?d+[VAC]$/.test(value)) {
        return value.slice(0, -1);
      }
      if (/^d*.?d+mV$/.test(value)) {
        return printValueTabular(Number.parseInt(value.slice(0, -2)) / 1000, omitUnits);
      }
      return value;
    }
    return EMPTY_CSV_VALUE;
  }

  /** Convert to JSON-serializable data structure.
   * @return {{entry: number, component: (string|RTCIceComponent), or: string, event_type: *, and: *, event_level: *, segment_activity: *, segment_id: *, event: Event, conditions: ({}|{}), timestamp: *}}
   */
  toJSON() {
    return {
      'entry': this.entry,
      'segment_id': this.segmentID,
      'segment_activity': this.segmentActivity,
      'timestamp': this.timestamp ? this.timestamp.toISOString() : null,
      'component': this.component,
      'event_type': this.eventType,
      'event_level': this.eventLevel,
      'event': this.event,
      'conditions': this.conditions
    };
  }
}

/**
 * @property {ZeroLogHeader} header
 * @property {[ZeroLogEntry]} entries
 */
export class ZeroLogData extends LogData {
  commonHeaders = [
    'entry',
    'segment_id',
    'segment_activity',
    'timestamp',
    'component',
    'event_type',
    'event_level',
    'event'
  ];

  /**
   * @param logLines {[string]}
   */
  constructor(logLines) {
    super([], []);
    this.header = new ZeroLogHeader(logLines);
    const dividerIndex = this.header.indexOfDividerLine(logLines);
    const numLines = logLines.length;
    this.entries = Array(numLines - dividerIndex);
    for (let lineIndex=dividerIndex; lineIndex < numLines; lineIndex++) {
      this.entries[lineIndex - dividerIndex] = new ZeroLogEntry(logLines[lineIndex], lineIndex);
    }
    this.annotateSegmentEntryInfo();
    this.tabularHeaderLabels = this.commonHeaders.concat(this.allConditionKeys);
  }

  /** Auto-increment a numeric ID for each sequence of entries for a closed contactor.
   */
  annotateSegmentEntryInfo() {
    let currentSegmentID = 0;
    let currentSegmentActivity = 'STOPPED';
    this.entries.forEach((entry) => {
      if (entry.isContactorCloseEntry()) {
        currentSegmentActivity = 'STARTED';
        currentSegmentID++;
      } else if (entry.isContactorOpenEntry()) {
        currentSegmentActivity = 'STOPPED';
        currentSegmentID++;
      } else if (entry.isRunningEntry() && currentSegmentActivity !== 'RIDING') {
        currentSegmentActivity = 'RIDING';
        currentSegmentID++;
      } else if (entry.isChargingEntry() && currentSegmentActivity !== 'CHARGING') {
        currentSegmentActivity = 'CHARGING';
        currentSegmentID++;
      }
      entry.segmentID = currentSegmentID;
      entry.segmentActivity = currentSegmentActivity;
    });
  }

  /** Return data labels used across all log entries for tabular output.
   * @returns {[string]}
   */
  get allConditionKeys() {
    const allKeys = [];
    this.entries.forEach((entry) => {
      Object.keys(entry.conditions).forEach((key) => {
        if (!allKeys.includes(key)) {
          allKeys.push(key);
        }
      });
    });
    return allKeys;
  }

  toJSON() {
    return {
      header: this.header.toJSON(),
      entries: this.entries.map((logEntry) => logEntry.toJSON())
    };
  }
}

export class JoinedLogData extends LogData {
  /** @type {LogData} */
  primaryLogData;
  /** @type {Object.<string, LogData>} */
  secondaryLogs = {};
  /** @type {[LogEntry|ZeroLogEntry]} */
  sortedEntries = [];

  constructor(primaryLog, secondaryLogs) {
    super([], []);
    this.primaryLogData = primaryLog;
    this.secondaryLogs = secondaryLogs;
    this.refresh();
  }

  get allEntriesByTimestamp() {
    let allEntries = this.primaryLogData.entries;
    for (let [key, log] of this.secondaryLogs) {
      const logEntries = log.entries;
      logEntries.forEach((entry) => {
        entry.logTag = key;
      });
      allEntries = allEntries.concat(logEntries);
    }
    allEntries.sort(LogEntryCompare);
    return allEntries;
  }

  /** Update state from inputs. */
  refresh(deep=false) {
    if (deep) {
      this.primaryLogData.refresh();
      for (let [key, log] of this.secondaryLogs) {
        log.refresh();
      }
    }
    this.entries = this.allEntriesByTimestamp;
  }

  /** Synthesize a merged log entry for the given timestamp.
   * @param someTimestamp {Date}
   * @returns {LogEntry}
   */
  entryForTimestamp(someTimestamp) {
    const entries = this.entries;
    let low = 0, high = entries.length - 1;
    while (low < high) {
      const mid = Math.floor((low + high) / 2);
      if (someTimestamp < entries[mid].timestamp) {
        high = mid;
      } else {
        low = mid + 1;
        break;
      }
    }
    const mostRecentEntryBefore = entries[low];
    const nextEntryAfter = low < entries.length - 1 ? entries[low + 1] : null;
    return mostRecentEntryBefore;
  }
}
