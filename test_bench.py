
import sys, os
import serial
import time
from .motor_control import MotorControl
from .temp_control import TempControl

class Serial:
    def __init__(self, comm = 'COM3',timeout = None):
      self.serial_client = None
      self.timeout = None
    def connect_to_serial(self):
      serial_client = serial.Serial(self.comm, self.timeout)

    def reset_weight(self):
      serial_client.write('r'.encode())
      serial_client.reset_input_buffer()
      time.sleep(2)
       #print('Setting scale to zero: ' + str(float(ser.readline())))


if __name__ == "__main__":
    temp_control = TempControl()
    motor = MotorControl()
