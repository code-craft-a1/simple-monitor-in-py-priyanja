import unittest
from monitor import *


class MonitorTest(unittest.TestCase):
  def test_temperature(self):
    self.assertTrue(is_temperature_ok(98.6))
    self.assertFalse(is_temperature_ok(103))
    self.assertFalse(is_temperature_ok(94))
  
  def test_pulse(self):
    self.assertTrue(is_pulse_ok(70))
    self.assertFalse(is_pulse_ok(59))
    self.assertFalse(is_pulse_ok(101))

  def test_spo2(self):
    self.assertTrue(is_spo2_ok(95))
    self.assertFalse(is_spo2_ok(89))

  def test_vitals_ok(self):
    self.assertTrue(vitals_ok(98.1, 70, 98))
    
  
  def test_not_ok_when_any_vital_out_of_range(self):
    self.assertFalse(vitals_ok(99, 102, 70))
    self.assertFalse(vitals_ok(103, 70, 95))
    self.assertFalse(vitals_ok(98.6, 101, 95))
    self.assertFalse(vitals_ok(103, 101, 89))
    self.assertFalse(vitals_ok(99, 102, 70))


if __name__ == '__main__':
  unittest.main()
