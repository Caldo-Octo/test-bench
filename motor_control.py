import time
import serial
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder
from pymodbus.client.sync import ModbusTcpClient

class MotorControl:
    def __init__(self, speed = 1, accel = 10, decel = 10, current = 1):
        #MMC Values
        self.mmc_speed = 0
        self.mmc_accel = 0
        self.mmc_decel = 0
        self.mmc_current = 0
        self.motor_in_motion = False
        #Desired Values
        self.speed = speed
        self.accel = accel
        self.decel = decel
        if current > 2.5:
            raise ValueError("Current needs to be below 2.6 A")
        self.current = current
        self.rotations = 1
        self.dispense_amount = 0
        self.modbus_client = None
        self.serial_client = None
        self.axis = int(0x100)
        self.motor_on_reg = 262
        self.motor_in_motion_reg = 263
        self.move_motor_reg = 384
        self.jog_motor = 328
        self.abort = 265
        self.set_speed_reg = int(0x41) + axis -1 # From default MMI mapping
        self.set_accel_reg = int(0x43)  + axis -1
        self.set_decel_reg = int(0x45)  + axis -1
        self.set_current_reg = int(0x49)  + axis -1

    def read_input_data(self):
        modbus_client.open()
        result  = modbus_client.read_holding_registers(self.set_speed_reg, 8)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, Endian.Big, wordorder=Endian.Little)
        self.motor_in_motion = modbus_client.read_holding_registers(self.motor_in_motion_reg,1).registers[0]
        modbus_client.close()

    def set_motor_params(self, speed = 1.00 , accel = 10.00, deccel = 10.00, current = 2.1):
        self.speed = speed
        self.accel = accel
        self.decel = decel
        if current > 2.5:
            raise ValueError("Current needs to be below 2.6 A")
        self.current = current*10
        
        #Modbus Registers
        modbus_payload = [self.speed, self.accel, self. decel, self.current]
        modbus_client.open()
        modbus_client.write_registers(self.set_speed_reg, modbus_payload, skip_encode=True)
        modbus_client.close()

    def run_motor(self, rotations = [1]):
        modbus_client.open()
        modbus_client.write_register(self.motor_on_reg, 1)
        #function to run motor on desired axis a fixed number of rotations (64 bit double precision float)
        if not self.motor_in_motion:
            result  = modbus_client.write_registers(self.move_motor, rotations, skip_encode=True)
        modbus_client.close()
    
    def jog_motor(self, speed):
        self.speed = speed
        self.modbus_client.open()
        self.modbus_client.write_register(self.motor_on_reg, 1)
        self.modbus_client.write_registers(self.jog_motor, speed , skip_encode=True)
        self.modbus_client.close()

    def stop_motor(self):
        self.modbus_client.open()
        modbus_client.write_register(self.abort,1)
        modbus_client.write_register(self.motor_on_reg, 0)
        modbus_client.close()
    
    def connect_to_mmc(self):
        self.modbus_client = ModbusTcpClient('192.168.1.100', port = 502)

  

