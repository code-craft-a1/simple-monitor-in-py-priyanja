import unittest
from monitor import *


class MonitorTest(unittest.TestCase):
  def test_temperature(self):
    # Temperature range: 95-102
    self.assertTrue(is_vital_ok('temperature', 98.6))
    self.assertTrue(is_vital_ok('temperature', 95))
    self.assertTrue(is_vital_ok('temperature', 102))
    self.assertFalse(is_vital_ok('temperature', 103))
    self.assertFalse(is_vital_ok('temperature', 94))
  
  def test_pulse(self):
    # Pulse range: 60-100
    self.assertTrue(is_vital_ok('pulse', 70))
    self.assertTrue(is_vital_ok('pulse', 60))
    self.assertTrue(is_vital_ok('pulse', 100))
    self.assertFalse(is_vital_ok('pulse', 59))
    self.assertFalse(is_vital_ok('pulse', 101))

  def test_spo2(self):
    # SpO2 range: >=90 (no upper limit)
    self.assertTrue(is_vital_ok('spo2', 95))
    self.assertTrue(is_vital_ok('spo2', 90))
    self.assertTrue(is_vital_ok('spo2', 99))
    self.assertFalse(is_vital_ok('spo2', 89))

  def test_vitals_ok(self):
    vitals = {'temperature': 98.1, 'pulse': 70, 'spo2': 95}
    self.assertTrue(vitals_ok(vitals))
    
  def test_not_ok_when_any_vital_out_of_range(self):
    # Test various combinations of out-of-range vitals
    self.assertFalse(vitals_ok({'temperature': 103, 'pulse': 70, 'spo2': 95}))
    self.assertFalse(vitals_ok({'temperature': 94, 'pulse': 70, 'spo2': 95}))
    self.assertFalse(vitals_ok({'temperature': 98.6, 'pulse': 101, 'spo2': 95}))
    self.assertFalse(vitals_ok({'temperature': 98.6, 'pulse': 59, 'spo2': 95}))
    self.assertFalse(vitals_ok({'temperature': 98.6, 'pulse': 70, 'spo2': 89}))
    self.assertFalse(vitals_ok({'temperature': 103, 'pulse': 101, 'spo2': 89}))

  def test_check_vital_function(self):
    # Test the check_vital function which handles alerts
    self.assertTrue(check_vital('temperature', 98.6))
    self.assertFalse(check_vital('temperature', 103))
    self.assertTrue(check_vital('pulse', 70))
    self.assertFalse(check_vital('pulse', 101))
    self.assertTrue(check_vital('spo2', 95))
    self.assertFalse(check_vital('spo2', 89))

  # New tests for warning functionality
  def test_warning_range_calculation(self):
    # Test warning range calculations
    temp_ranges = calculate_warning_ranges('temperature')
    # Temperature: 95-102, tolerance = 1.5% of 102 = 1.53
    # Low warning: 95 to 96.53, High warning: 100.47 to 102
    self.assertAlmostEqual(temp_ranges['warning_low_range'][1], 96.53, places=2)
    self.assertAlmostEqual(temp_ranges['warning_high_range'][0], 100.47, places=2)
    
    pulse_ranges = calculate_warning_ranges('pulse')
    # Pulse: 60-100, tolerance = 1.5% of 100 = 1.5
    # Low warning: 60 to 61.5, High warning: 98.5 to 100
    self.assertAlmostEqual(pulse_ranges['warning_low_range'][1], 61.5, places=1)
    self.assertAlmostEqual(pulse_ranges['warning_high_range'][0], 98.5, places=1)
    
    spo2_ranges = calculate_warning_ranges('spo2')
    # SpO2: >=90, tolerance = 1.5% of 100 = 1.5
    # Low warning: 90 to 91.5, No high warning
    self.assertAlmostEqual(spo2_ranges['warning_low_range'][1], 91.5, places=1)
    self.assertIsNone(spo2_ranges['warning_high_range'])

  def test_temperature_warning_detection(self):
    # Test temperature warning detection
    self.assertEqual(is_in_warning_range('temperature', 96.0), 'low')  # Low warning
    self.assertEqual(is_in_warning_range('temperature', 101.0), 'high')  # High warning
    self.assertFalse(is_in_warning_range('temperature', 98.6))  # Normal range
    self.assertFalse(is_in_warning_range('temperature', 94.0))  # Critical low
    self.assertFalse(is_in_warning_range('temperature', 103.0))  # Critical high

  def test_pulse_warning_detection(self):
    # Test pulse warning detection
    self.assertEqual(is_in_warning_range('pulse', 61.0), 'low')  # Low warning
    self.assertEqual(is_in_warning_range('pulse', 99.0), 'high')  # High warning
    self.assertFalse(is_in_warning_range('pulse', 75.0))  # Normal range
    self.assertFalse(is_in_warning_range('pulse', 58.0))  # Critical low
    self.assertFalse(is_in_warning_range('pulse', 105.0))  # Critical high

  def test_spo2_warning_detection(self):
    # Test SpO2 warning detection
    self.assertEqual(is_in_warning_range('spo2', 91.0), 'low')  # Low warning
    self.assertFalse(is_in_warning_range('spo2', 95.0))  # Normal range
    self.assertFalse(is_in_warning_range('spo2', 88.0))  # Critical low

  def test_check_vital_with_warning_function(self):
    # Test the check_vital_with_warning function returns
    # Temperature tests
    self.assertEqual(check_vital_with_warning('temperature', 98.6), 'ok')
    self.assertEqual(check_vital_with_warning('temperature', 96.0), 'warning')
    self.assertEqual(check_vital_with_warning('temperature', 101.0), 'warning')
    self.assertEqual(check_vital_with_warning('temperature', 94.0), 'critical')
    self.assertEqual(check_vital_with_warning('temperature', 103.0), 'critical')
    
    # Pulse tests
    self.assertEqual(check_vital_with_warning('pulse', 75.0), 'ok')
    self.assertEqual(check_vital_with_warning('pulse', 61.0), 'warning')
    self.assertEqual(check_vital_with_warning('pulse', 99.0), 'warning')
    self.assertEqual(check_vital_with_warning('pulse', 58.0), 'critical')
    self.assertEqual(check_vital_with_warning('pulse', 105.0), 'critical')
    
    # SpO2 tests
    self.assertEqual(check_vital_with_warning('spo2', 95.0), 'ok')
    self.assertEqual(check_vital_with_warning('spo2', 91.0), 'warning')
    self.assertEqual(check_vital_with_warning('spo2', 88.0), 'critical')

  def test_legacy_check_vital_with_warnings(self):
    # Test that legacy check_vital function treats warnings as acceptable
    self.assertTrue(check_vital('temperature', 96.0))  # Warning should return True
    self.assertTrue(check_vital('temperature', 101.0))  # Warning should return True
    self.assertFalse(check_vital('temperature', 94.0))  # Critical should return False
    self.assertFalse(check_vital('temperature', 103.0))  # Critical should return False

  def test_vitals_ok_with_warnings(self):
    # Test that vitals_ok accepts warnings but rejects critical values
    vitals_with_warning = {'temperature': 96.0, 'pulse': 70, 'spo2': 95}
    self.assertTrue(vitals_ok(vitals_with_warning))  # Should accept warnings
    
    vitals_critical = {'temperature': 94.0, 'pulse': 70, 'spo2': 95}
    self.assertFalse(vitals_ok(vitals_critical))  # Should reject critical

  def test_warning_tolerance_percentage(self):
    # Test that the warning tolerance is correctly set to 1.5%
    self.assertEqual(WARNING_TOLERANCE_PERCENT, 1.5)


if __name__ == '__main__':
  unittest.main()
