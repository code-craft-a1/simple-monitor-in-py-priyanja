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
    unit_upper = unit.upper()
    if unit_upper == 'C':
        return celsius_to_fahrenheit(value)
    if unit_upper == 'F':
        return value
    raise ValueError(f"Unsupported temperature unit: {unit}. Use 'C' or 'F'.")

def _needs_temperature_conversion(vital_name, unit):
    """Check if vital needs temperature unit conversion."""
    return vital_name == 'temperature' and unit is not None

def normalize_vital_value(vital_name, value, unit=None):
    """Convert vital value to standard unit if needed."""
    if _needs_temperature_conversion(vital_name, unit):
        return normalize_temperature(value, unit)
    # Default case - no conversion needed for pulse, spo2, or temperature without unit
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

def _has_both_limits(vital):
    """Check if vital has both min and max limits."""
    return vital['min'] is not None and vital['max'] is not None

def _check_range_with_both_limits(normalized_value, vital):
    """Check if value is within range when both min and max are defined."""
    return vital['min'] <= normalized_value <= vital['max']

def _check_range_with_max_only(normalized_value, vital):
    """Check if value is within range when only max is defined."""
    return normalized_value <= vital['max']

def _check_range_with_min_only(normalized_value, vital):
    """Check if value is within range when only min is defined."""
    return normalized_value >= vital['min']

def is_vital_ok(vital_name, value, unit=None):
    """Check if vital is within normal range."""
    normalized_value = normalize_vital_value(vital_name, value, unit)
    vital = VITAL_RANGES[vital_name]
    
    if _has_both_limits(vital):
        return _check_range_with_both_limits(normalized_value, vital)
    if vital['min'] is None:
        return _check_range_with_max_only(normalized_value, vital)
    return _check_range_with_min_only(normalized_value, vital)

def _check_low_warning_range(normalized_value, warning_ranges):
    """Check if value is in low warning range."""
    if not warning_ranges['warning_low_range']:
        return False
    low_min, low_max = warning_ranges['warning_low_range']
    return low_min <= normalized_value <= low_max

def _check_high_warning_range(normalized_value, warning_ranges):
    """Check if value is in high warning range."""
    if not warning_ranges['warning_high_range']:
        return False
    high_min, high_max = warning_ranges['warning_high_range']
    return high_min <= normalized_value <= high_max

def is_in_warning_range(vital_name, value, unit=None):
    """Check if vital is in warning range."""
    normalized_value = normalize_vital_value(vital_name, value, unit)
    warning_ranges = calculate_warning_ranges(vital_name)
    
    if _check_low_warning_range(normalized_value, warning_ranges):
        return 'low'
    if _check_high_warning_range(normalized_value, warning_ranges):
        return 'high'
    return False

def _format_display_value(value, vital_name, unit):
    """Format the display value with appropriate unit."""
    if vital_name == 'temperature' and unit:
        return f"{value}°{unit.upper()}"
    return str(value)

def _handle_warning_in_range(warning_type, vital_name, display_value):
    """Handle warning message display and return appropriate status."""
    if warning_type == 'low':
        warning_message(f"{VITAL_RANGES[vital_name]['warning_low']} (Value: {display_value})")
        return 'warning'
    if warning_type == 'high':
        warning_message(f"{VITAL_RANGES[vital_name]['warning_high']} (Value: {display_value})")
        return 'warning'
    return 'ok'

def check_vital_with_warning(vital_name, value, unit=None):
    """Check vital and display appropriate warning or alert."""
    display_value = _format_display_value(value, vital_name, unit)
    
    if is_vital_ok(vital_name, value, unit):
        warning_type = is_in_warning_range(vital_name, value, unit)
        return _handle_warning_in_range(warning_type, vital_name, display_value)
    
    alert_message(f"{VITAL_RANGES[vital_name]['alert']} (Value: {display_value})")
    return 'critical'

def check_vital(vital_name, value, unit=None):
    result = check_vital_with_warning(vital_name, value, unit)
    return result == 'ok' or result == 'warning'

def _is_unit_format(vital_data):
    """Check if vital data is in unit format (dictionary with 'value' key)."""
    return isinstance(vital_data, dict) and 'value' in vital_data

def _extract_vital_data(vital_data):
    """Extract value and unit from vital data, handling both formats."""
    if _is_unit_format(vital_data):
        return vital_data['value'], vital_data.get('unit', None)
    return vital_data, None

def vitals_ok(vitals):
    """Check all vitals and return True if all are OK or just warnings.
    
    vitals can be:
    - Simple format: {'temperature': 98.6, 'pulse': 70, 'spo2': 95}
    - With units: {'temperature': {'value': 37, 'unit': 'C'}, 'pulse': 70, 'spo2': 95}
    """
    for vital_name, vital_data in vitals.items():
        value, unit = _extract_vital_data(vital_data)
        if not check_vital(vital_name, value, unit):
            return False
    return True