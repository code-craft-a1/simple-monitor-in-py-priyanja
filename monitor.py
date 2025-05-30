from time import sleep
import sys

VITAL_RANGES = {
    'temperature': {
        'min': 95, 'max': 102, 
        'alert': 'Temperature critical!',
        'warning_low': 'Warning: Approaching hypothermia',
        'warning_high': 'Warning: Approaching hyperthermia'
    },
    'pulse': {
        'min': 60, 'max': 100, 
        'alert': 'Pulse Rate is out of range!',
        'warning_low': 'Warning: Approaching low pulse rate',
        'warning_high': 'Warning: Approaching high pulse rate'
    },
    'spo2': {
        'min': 90, 'max': None, 
        'alert': 'Oxygen Saturation out of range!',
        'warning_low': 'Warning: Approaching low oxygen saturation',
        'warning_high': None
    }, 
}

WARNING_TOLERANCE_PERCENT = 1.5

def calculate_warning_ranges(vital_name):
    """Calculate warning ranges based on 1.5% tolerance of upper limit."""
    vital = VITAL_RANGES[vital_name]
    min_val, max_val = vital['min'], vital['max']
    
    if max_val is not None:
        tolerance = max_val * WARNING_TOLERANCE_PERCENT / 100
        warning_low_max = min_val + tolerance if min_val is not None else None
        warning_high_min = max_val - tolerance
        return {
            'warning_low_range': (min_val, warning_low_max) if min_val is not None else None,
            'warning_high_range': (warning_high_min, max_val)
        }
    else:
        # For spo2 which has no upper limit, only calculate lower warning
        if min_val is not None:
            # Use a reasonable upper value for calculation (e.g., 100 for spo2)
            assumed_max = 100 if vital_name == 'spo2' else min_val * 2
            tolerance = assumed_max * WARNING_TOLERANCE_PERCENT / 100
            warning_low_max = min_val + tolerance
            return {
                'warning_low_range': (min_val, warning_low_max),
                'warning_high_range': None
            }
    return {'warning_low_range': None, 'warning_high_range': None}

def warning_message(message):
    """Display warning message."""
    print(f"⚠️  {message}")

def alert_message(message):
    print(message)
    for i in range(6):
        print('\r* ', end='')
        sys.stdout.flush()
        sleep(1)
        print('\r *', end='')
        sys.stdout.flush()
        sleep(1)

def is_vital_ok(vital_name, value):
    """Check if vital is within normal range."""
    vital = VITAL_RANGES[vital_name]
    if vital['min'] is not None and vital['max'] is not None :
      return vital['min'] <= value <= vital['max']
    elif vital['min'] is None : 
      return value<=vital['max']
    elif vital['max'] is None:
      return value>=vital['min']

def is_in_warning_range(vital_name, value):
    """Check if vital is in warning range."""
    warning_ranges = calculate_warning_ranges(vital_name)
    
    # Check lower warning range (
    if warning_ranges['warning_low_range']:
        low_min, low_max = warning_ranges['warning_low_range']
        if low_min <= value <= low_max:
            return 'low'
    
    # Check upper warning range 
    if warning_ranges['warning_high_range']:
        high_min, high_max = warning_ranges['warning_high_range']
        if high_min <= value <= high_max:
            return 'high'
    
    return False

def check_vital_with_warning(vital_name, value):
    """Check vital and display appropriate warning or alert."""
    if is_vital_ok(vital_name, value):
        # Value is in normal range, check if it's in warning zone
        warning_type = is_in_warning_range(vital_name, value)
        if warning_type == 'low':
            warning_message(VITAL_RANGES[vital_name]['warning_low'])
            return 'warning'
        elif warning_type == 'high':
            warning_message(VITAL_RANGES[vital_name]['warning_high'])
            return 'warning'
        else:
            return 'ok'
    else:
        # Value is outside normal range - this is critical
        alert_message(VITAL_RANGES[vital_name]['alert'])
        return 'critical'

def check_vital(vital_name, value):
    result = check_vital_with_warning(vital_name, value)
    return result == 'ok' or result == 'warning'

def vitals_ok(vitals):
    """Check all vitals and return True if all are OK or just warnings."""
    return all(check_vital(vital,value) for vital,value in vitals.items())