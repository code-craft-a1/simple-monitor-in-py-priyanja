from time import sleep
import sys

VITAL_RANGES = {
    'temperature': {'min': 95, 'max': 102,'alert': 'Temperature critical!'},
    'pulse': {'min': 60, 'max': 100,'alert': 'Pulse Rate is out of range!'},
    'spo2': {'min': 90, 'max': None,'alert': 'Oxygen Saturation out of range!'}, 
}

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
    vital = VITAL_RANGES[vital_name]
    if vital['min'] is not None and vital['max'] is not None :
      return vital['min'] <= value <= vital['max']
    elif vital['min'] is None : 
      return value<=vital['max']
    elif vital['max'] is None:
      return value>=vital['min']


def check_vital(vital_name,value):
    if not is_vital_ok(vital_name,value):
        alert_message(VITAL_RANGES[vital_name]['alert'])
        return False
    return True

def vitals_ok(vitals):
    return all(check_vital(vital,value) for vital,value in vitals.items())