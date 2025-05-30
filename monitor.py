
from time import sleep
import sys

def is_temperature_ok(temperature):
  return 95 <= temperature <= 102

def alert_message(message):
  print(message)
  for i in range(6):
    print('\r* ', end='')
    sys.stdout.flush()
    sleep(1)
    print('\r *', end='')
    sys.stdout.flush()
    sleep(1)

def is_pulse_ok(pulse):
  return 60 <= pulse <= 100

def is_spo2_ok(spo2):
  return spo2>=90

def vitals_ok(temperature, pulseRate, spo2):
  are_vitals_ok=True
  if not is_temperature_ok(temperature):
    alert_message('Temperature critical!')
    are_vitals_ok= False
  if not is_pulse_ok(pulseRate):
    alert_message('Pulse Rate is out of range!')
    are_vitals_ok= False
  if not is_spo2_ok(spo2):
    alert_message('Oxygen Saturation out of range!')
    are_vitals_ok= False
  return are_vitals_ok

