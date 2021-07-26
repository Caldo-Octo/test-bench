# python -c "from MotorTest import run_motor; run_motor()"
# python -c "from MotorTest import set_temperature; set_temperature();"
# python -c "from MotorTest import set_motor_params; set_motor_params()"
# python -c "from MotorTest import dispense_pattern; dispense_pattern()"
# python -c "from MotorTest import stop_motor; stop_motor()"
# python -c "from MotorTest import run_pump; run_pump()"



from pymodbus.client.sync import ModbusTcpClient
import sys, os
import pyads
import time
import serial
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
import matplotlib.pyplot as plt

plc = pyads.Connection('127.0.0.1.1.1', pyads.PORT_TC3PLC1)
plc.open()

def set_temperature(temperature = 630, band = 20, samples = 50):
    plc.write_by_name('GVL.setpoint',(temperature))
    plc.write_by_name('main.tempband',(band))
    plc.write_by_name('GVL.tempOn',True)
    curr = plc.read_by_name('main.temp1')
    #see_temperature_history(samples)
    print("New Target Temp: " + str(temperature))
    print("Current Temp: " + str(curr))


def see_temperature_history(samples = 200):
    #curr = plc.read_by_name('main.temp1')
    plt.axis([0, samples, 200, 1500])

    for i in range(samples):
        y =  plc.read_by_name('main.temp1')
        plt.scatter(i, y)
        plt.pause(0.05)

    plt.show()

ser = serial.Serial('COM3', timeout = None)

def dispense_weight(amount = 15.0, speed = .25):
    client = ModbusTcpClient('192.168.1.100',port = 502)
    reset_weight()
    total = 0
    while total <= amount:
        jog_motor(speed)
        ser.reset_input_buffer()
        data = ser.readline()
        total = float(data)
        print(total)
    stop_motor()
    print("Grams dispensed: " + str(total))
    return total

def reset_weight():
   ser.write('r'.encode())
   ser.reset_input_buffer()
   time.sleep(2)
   print('Setting scale to zero: ' + str(float(ser.readline())))

def run_pump():
   ser.write('a'.encode())
   time.sleep(2)
   print('Pumped 1 revolution')


def stop_motor():
    abort_motor = 265
    client.write_register(abort_motor,1)
    client.write_register(262, 0)


def jog_motor(speed):
    move_motor = 328
    builder = BinaryPayloadBuilder(byteorder='>',wordorder='<')
    client.write_register(262, 1)
    builder.add_32bit_float(speed)
    payload = builder.build()
    result  = client.write_registers(move_motor, payload, skip_encode=True)



client = ModbusTcpClient('192.168.1.100', port = 502)


def set_motor_params(speed = 1.00 ,accel = 10.00, deccel = 10.00, current = 2.1):
    if current >= 3:
        current = 2.6
        print("Exceeded current limit, setting motor current to 2.6A")
    axis = int(0x100)
    client = ModbusTcpClient('192.168.1.100', port = 502)
    set_speed = int(0x41) + axis -1 # From default MMI mapping
    set_accel = int(0x43)  + axis -1
    set_deccel = int(0x45)  + axis -1
    set_current = int(0x49)  + axis -1
    builder1 = BinaryPayloadBuilder(byteorder='>',wordorder='<')
    builder1.add_32bit_float(speed) # Writing to 32bit single precision floats
    builder1.add_32bit_float(accel)
    builder1.add_32bit_float(deccel)
    builder1.add_32bit_float(current)
    payload1 = builder1.build()
    result  = client.write_registers(set_speed, payload1, skip_encode=True)
    # read floats
    result  = client.read_holding_registers(set_speed, 8)
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, Endian.Big, wordorder=Endian.Little)
    client.close()
    print("New speed: " + str(decoder.decode_32bit_float()))

    return result.registers

def run_motor(rotations = [1.0000]):
    axis = int(0x100)
    client = ModbusTcpClient('192.168.1.100', port = 502)
    client.write_register(262, 1)
    #function to run motor on desired axis a fixed number of rotations (64 bit double precision float)
    move_motor = 384 # Address of BeginMotorBy
    for cmd in rotations:
        while client.read_holding_registers(263,1).registers[0] == 0:
            time.sleep(.05)
        if client.read_holding_registers(263,1).registers[0] == 1:
            builder = BinaryPayloadBuilder(byteorder='>',wordorder='<')
            builder.add_64bit_float(cmd) # 64 bit double precision float
            payload = builder.build()
            result  = client.write_registers(move_motor, payload, skip_encode=True)
            print("Rotations Done: " + str(cmd))

    # read floats
    result  = client.read_holding_registers(move_motor, 4)
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, Endian.Big, wordorder=Endian.Little)

    client.close()
    print("Done")

    return result.registers

def dispense_pattern(amount = 50.0, pattern = [1.4,-.9,1.4,-.9,1.4,-.9,1.4,-.9]):
    axis = int(0x100)
    reset_weight()
    total = 0
    client = ModbusTcpClient('192.168.1.100', port = 502)
    client.write_register(262, 1)
    #function to run motor on desired axis a fixed number of rotations (64 bit double precision float)
    move_motor = 384 # Address of BeginMotorBy
    while True:
        for cmd in pattern:
            while client.read_holding_registers(263,1).registers[0] == 0:
                time.sleep(.05)
                ser.reset_input_buffer()
                data = ser.readline()
                total = float(data)
                print("Current Weight: " + str(total))
                if total >= amount:
                    print("Weight Achieved: " + str(total))
                    value = input("Continue? [Y/N]")
                    if value == "Y":
                        reset_weight()
                        total = 0
                        continue

            if client.read_holding_registers(263,1).registers[0] == 1:
                builder = BinaryPayloadBuilder(byteorder='>',wordorder='<')
                builder.add_64bit_float(cmd) # 64 bit double precision float
                payload = builder.build()
                result  = client.write_registers(move_motor, payload, skip_encode=True)
                print("Rotations Done: " + str(cmd))

    # read floats
    result  = client.read_holding_registers(move_motor, 4)
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, Endian.Big, wordorder=Endian.Little)

    client.close()
    print("Done")


if client.connect():
    print("MMC is connected!")
else:
    print("Connection Error")
