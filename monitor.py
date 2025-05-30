from time import sleep
import sys

# Standard units and ranges (temperature in Fahrenheit)
VITAL_RANGES = {
    'temperature': {
        'min': 95, 'max': 102, 
        'standard_unit': 'F',
        'alert': 'Temperature critical!',
        'warning_low': 'Warning: Approaching hypothermia',
        'warning_high': 'Warning: Approaching hyperthermia'
    },
    'pulse': {
        'min': 60, 'max': 100, 
        'standard_unit': 'bpm',
        'alert': 'Pulse Rate is out of range!',
        'warning_low': 'Warning: Approaching low pulse rate',
        'warning_high': 'Warning: Approaching high pulse rate'
    },
    'spo2': {
        'min': 90, 'max': None, 
        'standard_unit': '%',
        'alert': 'Oxygen Saturation out of range!',
        'warning_low': 'Warning: Approaching low oxygen saturation',
        'warning_high': None
    }, 
}

WARNING_TOLERANCE_PERCENT = 1.5

# Unit conversion functions
def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32


def normalize_temperature(value, unit):
    """Convert temperature to standard unit (Fahrenheit)."""
    if unit.upper() == 'C':
        return celsius_to_fahrenheit(value)
    elif unit.upper() == 'F':
        return value
    else:
        raise ValueError(f"Unsupported temperature unit: {unit}. Use 'C' or 'F'.")

def normalize_vital_value(vital_name, value, unit=None):
    """Convert vital value to standard unit if needed."""
    if vital_name == 'temperature' and unit is not None:
        return normalize_temperature(value, unit)
    elif vital_name in ['pulse', 'spo2']:
        # These don't need unit conversion currently
        return value
    # Default case - no conversion needed
    return value

def _calculate_tolerance(max_val):
    """Calculate tolerance value based on maximum value."""
    return max_val * WARNING_TOLERANCE_PERCENT / 100

def _get_warning_range_or_none(min_val, max_val):
    """Return warning range tuple or None if min_val is None."""
    return (min_val, max_val) if min_val is not None else None

def _calculate_ranges_with_max(min_val, max_val):
    """Calculate warning ranges for vitals that have both min and max values."""
    tolerance = _calculate_tolerance(max_val)
    warning_low_max = min_val + tolerance if min_val is not None else None
    warning_high_min = max_val - tolerance
    return {
        'warning_low_range': _get_warning_range_or_none(min_val, warning_low_max),
        'warning_high_range': (warning_high_min, max_val)
    }

def _calculate_ranges_without_max(vital_name, min_val):
    """Calculate warning ranges for vitals that only have minimum values (like spo2)."""
    if min_val is None:
        return {'warning_low_range': None, 'warning_high_range': None}
    
    assumed_max = 100 if vital_name == 'spo2' else min_val * 2
    tolerance = _calculate_tolerance(assumed_max)
    warning_low_max = min_val + tolerance
    return {
        'warning_low_range': (min_val, warning_low_max),
        'warning_high_range': None
    }

def calculate_warning_ranges(vital_name):
    """Calculate warning ranges based on 1.5% tolerance of upper limit."""
    vital = VITAL_RANGES[vital_name]
    min_val, max_val = vital['min'], vital['max']
    
    if max_val is not None:
        return _calculate_ranges_with_max(min_val, max_val)
    return _calculate_ranges_without_max(vital_name, min_val)

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

def is_vital_ok(vital_name, value, unit=None):
    """Check if vital is within normal range."""
    normalized_value = normalize_vital_value(vital_name, value, unit)
    vital = VITAL_RANGES[vital_name]
    if vital['min'] is not None and vital['max'] is not None :
      return vital['min'] <= normalized_value <= vital['max']
    elif vital['min'] is None : 
      return normalized_value<=vital['max']
    elif vital['max'] is None:
      return normalized_value>=vital['min']

def is_in_warning_range(vital_name, value, unit=None):
    """Check if vital is in warning range."""
    normalized_value = normalize_vital_value(vital_name, value, unit)
    warning_ranges = calculate_warning_ranges(vital_name)
    
    # Check lower warning range (
    if warning_ranges['warning_low_range']:
        low_min, low_max = warning_ranges['warning_low_range']
        if low_min <= normalized_value <= low_max:
            return 'low'
    
    # Check upper warning range 
    if warning_ranges['warning_high_range']:
        high_min, high_max = warning_ranges['warning_high_range']
        if high_min <= normalized_value <= high_max:
            return 'high'
    
    return False

def check_vital_with_warning(vital_name, value, unit=None):
    """Check vital and display appropriate warning or alert."""
    # Format the value with unit for display
    display_value = f"{value}°{unit.upper()}" if vital_name == 'temperature' and unit else str(value)
    
    # First check if it's in normal range
    if is_vital_ok(vital_name, value, unit):
        # Value is in normal range, check if it's in warning zone
        warning_type = is_in_warning_range(vital_name, value, unit)
        if warning_type == 'low':
            warning_message(f"{VITAL_RANGES[vital_name]['warning_low']} (Value: {display_value})")
            return 'warning'
        elif warning_type == 'high':
            warning_message(f"{VITAL_RANGES[vital_name]['warning_high']} (Value: {display_value})")
            return 'warning'
        else:
            return 'ok'
    else:
        # Value is outside normal range - this is critical
        alert_message(f"{VITAL_RANGES[vital_name]['alert']} (Value: {display_value})")
        return 'critical'

def check_vital(vital_name, value, unit=None):
    result = check_vital_with_warning(vital_name, value, unit)
    return result == 'ok' or result == 'warning'

def vitals_ok(vitals):
    """Check all vitals and return True if all are OK or just warnings.
    
    vitals can be:
    - Simple format: {'temperature': 98.6, 'pulse': 70, 'spo2': 95}
    - With units: {'temperature': {'value': 37, 'unit': 'C'}, 'pulse': 70, 'spo2': 95}
    """
    for vital_name, vital_data in vitals.items():
        if isinstance(vital_data, dict) and 'value' in vital_data:
            # New format with units
            value = vital_data['value']
            unit = vital_data.get('unit', None)
        else:
            # Legacy format - just the value
            value = vital_data
            unit = None
        
        if not check_vital(vital_name, value, unit):
            return False
    return True