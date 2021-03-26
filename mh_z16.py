import serial
import time


class Mh_Z16:
    """
    Infrared CO2 Sensor 0-50000ppm SKU SEN0220 Python module
    https://wiki.dfrobot.com/Infrared_CO2_Sensor_0-50000ppm_SKU__SEN0220
    """
    
    READ_CMD = [0xFF,0x1,0x86,0x0,0x0,0x0,0x0,0x0,0x79]
    FRAME_LENGHT = 9
    START_BYTE = 'ff'
    FIRST_BYTE_DATA = 1
    LAST_BYTE_DATA = 8
    CHECKSUM_BYTE = 8
    
    def __init__(self, serial_port='/dev/ttyS0'):
        self.serial_port= serial_port
        self.hex_datas = []
        self.co2_level = None
        self.computed_checksum = None

    def read_serial_hex_datas(self) -> list:
        self.hex_datas = []
        with serial.Serial(self.serial_port, 9600, timeout=1) as ser:
            ser.write(Mh_Z16.READ_CMD)
            time.sleep(0.5)
            for i in range(0, 9):
                if ser.in_waiting > 0:
                    self.hex_datas.append(ser.read().hex())
    
    def calc_co2_level(self) -> int:
        self.co2_level = None
        if len(self.hex_datas) != Mh_Z16.FRAME_LENGHT:
            raise ValueError('Frame lenght error')
        if self.hex_datas[0] != Mh_Z16.START_BYTE or int(self.hex_datas[1], 16) != Mh_Z16.READ_CMD[2]:
            raise ValueError('Frame START or CMD BYTE error')
        msb = int(self.hex_datas[2], 16)
        lsb = int(self.hex_datas[3], 16)
        self.co2_level = msb * 256 + lsb

    def calc_checksum(self) -> int:
        self.computed_checksum
        checksum = 0
        for i in range(Mh_Z16.FIRST_BYTE_DATA, Mh_Z16.LAST_BYTE_DATA):
            checksum += int(self.hex_datas[i], 16)
        checksum = checksum & 0xFF
        checksum = 0xFF - checksum
        checksum += 1
        self.computed_checksum = checksum

    def read_checksum(self) -> int:
        if len(self.hex_datas) != Mh_Z16.FRAME_LENGHT:
            return -1
        return int(self.hex_datas[Mh_Z16.CHECKSUM_BYTE], 16)

    def get_co2_level(self):
        self.read_serial_hex_datas()
        self.calc_co2_level()
        self.calc_checksum()
        frame_checksum = self.read_checksum()
        if self.computed_checksum == frame_checksum:
            return self.co2_level
        else:
            raise ValueError('Checksum error')


if __name__ == '__main__':
    
    sensor = Mh_Z16(serial_port='/dev/ttyS0')
    print('CO2 level:', sensor.get_co2_level())
    

