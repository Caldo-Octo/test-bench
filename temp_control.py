import pyads

class TempControl:
    def __init__(self):
        self.units = 'f'
        self.setpoint = 140
        self.band = 20
        self.plc_temp = 0
        self.temp_on = False
        self.actual_temp=0
        self.plc = None


    def set_temperature(self, setpoint, band):
        '''Translate input temp to a plc usable int'''
        if self.units == 'f':
            self.plc_temp = (self.setpoint-32)*(5/9)*10
        if self.units == 'c':
            self.plc_temp = self.setpoint*10

        self.plc.open()
        self.plc.write_by_name('GVL.setpoint',int(self.plc_temp))
        self.plc.write_by_name('main.tempband',int(self.band))
        self.plc.close()

    def connect_to_plc(self):
        self.plc = pyads.Connection('127.0.0.1.1.1', pyads.PORT_TC3PLC1)

    def read_from_plc(self):
        '''Read from PLC'''
        self.plc.open()
        self.actual_temp = plc.read_by_name('main.temp1')
        self.plc.close()


    def enable_heat(self):
        '''write vars to PLC'''
        #Only open plc comms when we want to update the temp.
        self.plc.open()
        self.plc.write_by_name('GVL.tempOn',self.temp_on)
        self.plc.close()
