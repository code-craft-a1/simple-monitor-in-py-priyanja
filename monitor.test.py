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


if __name__ == '__main__':
  unittest.main()
