#!/usr/bin/env python3

"""Decode a Zero Motorcycles VIN into usable attributes."""

YEARS_BY_CODE = {
    '9': 2009,
    'A': 2010,
    'B': 2011,
    'C': 2012,
    'D': 2013,
    'E': 2014,
    'F': 2015,
    'G': 2016,
    'H': 2017,
    'J': 2018,
    'K': 2019,
    'L': 2020,
    'M': 2021,
    'N': 2022,
    'P': 2023,
    'R': 2024,
    'S': 2025
}


MOTORS_BY_CODE = {
    'M3': '9.1kW',
    'ZA': '11kW 75-5',
    'ZB': '11kW 75-7',
    'Z1': '13kW',
    'Z2': '16kW 75-7',
    'Z3': '16kW 75-7R',
    'Z4': '17kW 75-5',
    'Z5': '21kW 75-7',
    'Z6': '21kW 75-7R',
    'Z7': '40kW 75-10R'
}


MODEL_LINES_BY_CODE = {
    'M2': 'S',
    'M3': 'S',
    'M4': 'S/SR/SP 8.5',
    'M5': 'S/SR/SP 11.4',
    'M7': 'S/SR/SP 9.4',
    'M8': 'S/SR/SP 12.5',
    'M9': 'S/SR/SP 13.0',
    'M0': 'S/SR/SP 9.8',
    'MB': 'S/SP 6.5',
    'MC': 'S/SR/SP/SRP 13.0',
    'MD': 'S 13.0 (11kW)',
    'ME': 'S 7.2 (11kW)',
    'MF': 'S/SR 14.4',
    'MG': 'S 14.4 (11kW)',
    'MH': 'S 7.2 (11kW)',
    'MK': 'S 14.4 (11kW)',
    'D2': 'DS',
    'D3': 'DS',
    'D4': 'DS',
    'D5': 'DS/DSR/DSP 11.4',
    'D6': 'DS/DSR/DSP 8.5',
    'D7': 'DS/DSR/DSP 9.4',
    'D8': 'DS/DSR/DSP 12.5',
    'D9': 'DS/DSR/DSP 13.0',
    'D0': 'DS/DSR/DSP 9.8',
    'DA': 'DS 6.5',
    'DB': 'DS/DSR/DSP/DSRP 13.0',
    'DC': 'DS 7.2 (11kW)',
    'DD': 'DS/DSR 14.4',
    'DE': 'DS 14.4 (11kW)',
    'DF': 'DS 7.2 (11kW)',
    'DH': 'DS 14.4 (11kW)',
    'X2': 'MX',
    'X3': 'FX',
    'X4': 'FX/FXL',
    'X5': 'FXP/FXLP',
    'X6': 'FX/FXS',
    'X7': 'FXP',
    'X8': 'FX/FXS',
    'X9': 'FXP',
    'XB': 'FX/FXS/FXP',
    'XC': 'FX/FXS/FXP',
    'C2': 'XU-LSM (CA)',
    'L2': 'XU-M (EU)',
    'U1': 'XU',
    'U2': 'XU',
    'U3': 'XU',
    'FA': 'SRF'
}


MODELS_BY_CODE = {
    'A': 'S',
    'B': 'DS',
    'C': 'FX',
    'E': 'XU',
    'G': 'SR/DSR',
    'H': 'FXP',
    'J': 'FXS',
    'K': 'SRF'
}


def decode_vin(vin: str) -> {}:
    """The metadata about the bike decoded from the VIN."""
    model_year = YEARS_BY_CODE[vin[9]]
    platform_code = vin[3]
    if platform_code == 'X':
        platform = 'XMX' if model_year > 2012 else platform_code
    elif platform_code == 'S':
        platform = 'SDS' if model_year > 2012 else platform_code
    elif platform_code == 'Z':
        platform = 'FST'
    else:
        platform = None
    model_line_parts = MODEL_LINES_BY_CODE[vin[4:6]].split(' ')
    model_from_line = model_line_parts[0]
    model_line_capacity = model_line_parts[1] if len(model_line_parts) > 1 else None
    model_line_power = model_line_parts[2] if len(model_line_parts) > 2 else None
    motor_parts = MOTORS_BY_CODE[vin[6:8]].split(' ', 2)
    motor_power = motor_parts[0] or model_line_power
    motor_size = motor_parts[1] if len(motor_parts) > 1 else None
    model = MODELS_BY_CODE[vin[11]]
    if '/' in model:
        # if model_from_line and '/' not in model_from_line.group(0):
        #     model = model_from_line.group(0)
        if model == 'SR/DSR':
            if 2013 < model_year < 2016:
                model = 'SR'
            else:
                model = 'DSR' if 'DS' in model_from_line else 'SR'
        if motor_size:
            if 'DS/DSR' in model:
                model = 'DSR' if motor_size == '75-7R' else 'DS'
            elif 'S/SR' in model:
                model = 'SR' if motor_size == '75-7R' else 'S'
    return {
        'manufacturer': 'Zero Motorcycles' if vin[:3] == '538' else None,
        'plant_location': 'Santa Cruz, CA' if vin[10] == 'C' else None,
        'year': model_year,
        'platform': platform,
        'model': model,
        'motor': {
            'power': motor_power,
            'size': motor_size
        },
        'pack_capacity': model_line_capacity
    }


if __name__ == '__main__':
    import argparse

    ARGS_PARSER = argparse.ArgumentParser()
    ARGS_PARSER.add_argument('vin',
                             help="the VIN to process")
    ARGS_PARSER.add_argument('--format', default='text',
                             choices=['json', 'text'],
                             help="the format to print the output")

    CLI_ARGS = ARGS_PARSER.parse_args()
    DECODED = decode_vin(CLI_ARGS.vin)
    FORMAT = CLI_ARGS.format
    if FORMAT == 'json':
        import json
        print(json.dumps(DECODED))
    elif FORMAT == 'text':
        def print_kv(label, value):
            """nicer print"""
            human_key = ' '.join(map(lambda x: x.capitalize(), label.split('_')))
            print('{}:\t{}'.format(human_key, value))
        for k, v in DECODED.items():
            if isinstance(v, dict):
                for k1, v1 in v.items():
                    print_kv(k.upper() + '_' + k1.upper(), v1)
            else:
                print_kv(k, v)
