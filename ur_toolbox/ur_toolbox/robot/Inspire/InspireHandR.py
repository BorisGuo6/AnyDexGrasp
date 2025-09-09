import numpy as np
import serial
from serial.tools import list_ports
import binascii
import time
import operator
import struct


which_finger_to_close = {'0':[0, 0, 0, 472, 523, 0],
                '1':[0, 0, 472, 472, 523, 0],
                '2':[0, 472, 472, 472, 523, 0],
                '3':[472, 472, 472, 472, 523, 0],
                '4':[1, 1, 1, 1, 1, 0],
                '5':[1, 1, 1, 1, 1, 0],
                '6':[0, 0, 0, 1, 1, 0],
                '7':[0, 0, 1, 1, 1, 0],
                '8':[0, 1, 1, 1, 1, 0],
                '9':[0, 1, 1, 0, 1, 0],
                '10':[0, 0, 0, 0, 1, 0],
                '11':[0, 0, 0, 0, 1, 0],
                }

class InspireHandR:
    def __init__(self, port = '/dev/ttyUSB0'):

        self.ser = serial.Serial(port, 115200)
        self.ser.isOpen()
        self.hand_id = 1
        power1 = 1000
        power2 = 1000
        power3 = 1000
        power4 = 1000
        power5 = 1000
        power6 = 1000
        self.setpower(power1, power2, power3, power4, power5, power6)

        speed1 = 1000
        speed2 = 1000
        speed3 = 1000
        speed4 = 1000
        speed5 = 1000
        speed6 = 1000
        self.setspeed(speed1, speed2, speed3, speed4, speed5, speed6)
        self.set_clear_error()
        self.f1_init_angle = 1000  # Little finger initial position
        self.f2_init_angle = 1000  # Ring finger initial position
        self.f3_init_angle = 1000  # Middle finger initial position
        self.f4_init_angle = 585  # Index finger initial position
        self.f5_init_angle = 545  # Thumb initial position
        self.f6_init_angle = 100  # Thumb rotates toward the palm initial position

        # Hand open, for testing
        # self.f1_init_pos = 0    # Little finger initial position
        # self.f2_init_pos = 0    # Ring finger initial position
        # self.f3_init_pos = 0    # Middle finger initial position
        # self.f4_init_pos = 0    # Index finger initial position
        # self.f5_init_pos = 0    # Thumb initial position
        # self.f6_init_pos = 0    # Thumb rotates toward the palm initial position
        # self.gesture_force_clb()
        self.reset()

    # Split data into high and low bytes
    def data2bytes(self, data):
        rdata = [0xff] * 2
        if data == -1:
            rdata[0] = 0xff
            rdata[1] = 0xff
        else:
            rdata[0] = data & 0xff
            rdata[1] = (data >> 8) & (0xff)
        return rdata

    # Convert hex/decimal number to bytes
    def num2str(self, num):
        str = hex(num)
        str = str[2:4]
        if (len(str) == 1):
            str = '0' + str
        str = bytes.fromhex(str)
        # print(str)
        return str

    # Calculate checksum
    def checknum(self, data, leng):
        result = 0
        for i in range(2, leng):
            result += data[i]
        result = result & 0xff
        # print(result)
        return result

    def setpos(self, pos1, pos2, pos3, pos4, pos5, pos6):
        global hand_id

        if pos1 < -1 or pos1 > 2000:
            print('Value out of valid range: -1 to 2000')
            return
        if pos2 < -1 or pos2 > 2000:
            print('Value out of valid range: -1 to 2000')
            return
        if pos3 < -1 or pos3 > 2000:
            print('Value out of valid range: -1 to 2000')
            return
        if pos4 < -1 or pos4 > 2000:
            print('Value out of valid range: -1 to 2000')
            return
        if pos5 < -1 or pos5 > 2000:
            print('Value out of valid range: -1 to 2000')
            return
        if pos6 < -1 or pos6 > 2000:
            print('Value out of valid range: -1 to 2000')
            return

        datanum = 0x0F
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Write operation
        b[4] = 0x12

        # Address
        b[5] = 0xC2
        b[6] = 0x05

        # Data
        b[7] = self.data2bytes(pos1)[0]
        b[8] = self.data2bytes(pos1)[1]

        b[9] = self.data2bytes(pos2)[0]
        b[10] = self.data2bytes(pos2)[1]

        b[11] = self.data2bytes(pos3)[0]
        b[12] = self.data2bytes(pos3)[1]

        b[13] = self.data2bytes(pos4)[0]
        b[14] = self.data2bytes(pos4)[1]

        b[15] = self.data2bytes(pos5)[0]
        b[16] = self.data2bytes(pos5)[1]

        b[17] = self.data2bytes(pos6)[0]
        b[18] = self.data2bytes(pos6)[1]

        # Checksum
        b[19] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)
        getdata = self.ser.read(9)

        return

    def setangle(self, angle1, angle2, angle3, angle4, angle5, angle6):
        if angle1 < -1 or angle1 > 1000:
            print('Value out of valid range: -1 to 1000')
            return
        if angle2 < -1 or angle2 > 1000:
            print('Value out of valid range: -1 to 1000')
            return
        if angle3 < -1 or angle3 > 1000:
            print('Value out of valid range: -1 to 1000')
            return
        if angle4 < -1 or angle4 > 1000:
            print('Value out of valid range: -1 to 1000')
            return
        if angle5 < -1 or angle5 > 1000:
            print('Value out of valid range: -1 to 1000')
            return
        if angle6 < -1 or angle6 > 1000:
            print('Value out of valid range: -1 to 1000')
            return

        datanum = 0x0F
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Write operation
        b[4] = 0x12

        # Address
        b[5] = 0xCE
        b[6] = 0x05

        # Data
        b[7] = self.data2bytes(angle1)[0]
        b[8] = self.data2bytes(angle1)[1]

        b[9] = self.data2bytes(angle2)[0]
        b[10] = self.data2bytes(angle2)[1]

        b[11] = self.data2bytes(angle3)[0]
        b[12] = self.data2bytes(angle3)[1]

        b[13] = self.data2bytes(angle4)[0]
        b[14] = self.data2bytes(angle4)[1]

        b[15] = self.data2bytes(angle5)[0]
        b[16] = self.data2bytes(angle5)[1]

        b[17] = self.data2bytes(angle6)[0]
        b[18] = self.data2bytes(angle6)[1]

        # Checksum
        b[19] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)
        getdata = self.ser.read(9)


    # Set force control thresholds
    def setpower(self, power1, power2, power3, power4, power5, power6):
        if power1 < 0 or power1 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if power2 < 0 or power2 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if power3 < 0 or power3 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if power4 < 0 or power4 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if power5 < 0 or power5 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if power6 < 0 or power6 > 1000:
            print('Value out of valid range: 0 to 1000')
            return

        datanum = 0x0F
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Write operation
        b[4] = 0x12

        # Address
        b[5] = 0xDA
        b[6] = 0x05

        # Data
        b[7] = self.data2bytes(power1)[0]
        b[8] = self.data2bytes(power1)[1]

        b[9] = self.data2bytes(power2)[0]
        b[10] = self.data2bytes(power2)[1]

        b[11] = self.data2bytes(power3)[0]
        b[12] = self.data2bytes(power3)[1]

        b[13] = self.data2bytes(power4)[0]
        b[14] = self.data2bytes(power4)[1]

        b[15] = self.data2bytes(power5)[0]
        b[16] = self.data2bytes(power5)[1]

        b[17] = self.data2bytes(power6)[0]
        b[18] = self.data2bytes(power6)[1]

        # Checksum
        b[19] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)
        getdata = self.ser.read(9)


    # Set speed
    def setspeed(self, speed1, speed2, speed3, speed4, speed5, speed6):
        if speed1 < 0 or speed1 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if speed2 < 0 or speed2 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if speed3 < 0 or speed3 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if speed4 < 0 or speed4 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if speed5 < 0 or speed5 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if speed6 < 0 or speed6 > 1000:
            print('Value out of valid range: 0 to 1000')
            return

        datanum = 0x0F
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Write operation
        b[4] = 0x12

        # Address
        b[5] = 0xF2
        b[6] = 0x05

        # Data
        b[7] = self.data2bytes(speed1)[0]
        b[8] = self.data2bytes(speed1)[1]

        b[9] = self.data2bytes(speed2)[0]
        b[10] = self.data2bytes(speed2)[1]

        b[11] = self.data2bytes(speed3)[0]
        b[12] = self.data2bytes(speed3)[1]

        b[13] = self.data2bytes(speed4)[0]
        b[14] = self.data2bytes(speed4)[1]

        b[15] = self.data2bytes(speed5)[0]
        b[16] = self.data2bytes(speed5)[1]

        b[17] = self.data2bytes(speed6)[0]
        b[18] = self.data2bytes(speed6)[1]

        # Checksum
        b[19] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)
        getdata = self.ser.read(9)
 

    # Read actual position values from the driver
    def get_setpos(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0xC2
        b[6] = 0x05

        # Length of registers to read
        b[7] = 0x0C

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(20)

        setpos = [0] * 6
        for i in range(1, 7):
            if getdata[i * 2 + 5] == 0xff and getdata[i * 2 + 6] == 0xff:
                setpos[i - 1] = -1
            else:
                setpos[i - 1] = getdata[i * 2 + 5] + (getdata[i * 2 + 6] << 8)
        return setpos

    # Read configured angles
    def get_setangle(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0xCE
        b[6] = 0x05

        # Length of registers to read
        b[7] = 0x0C

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(20)

        setangle = [0] * 6
        for i in range(1, 7):
            if getdata[i * 2 + 5] == 0xff and getdata[i * 2 + 6] == 0xff:
                setangle[i - 1] = -1
            else:
                setangle[i - 1] = getdata[i * 2 + 5] + (getdata[i * 2 + 6] << 8)
        return setangle

    # Read configured force control thresholds from the driver
    def get_setpower(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0xDA
        b[6] = 0x05

        # Length of registers to read
        b[7] = 0x0C

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)
        getdata = self.ser.read(20)


        setpower = [0] * 6
        for i in range(1, 7):
            if getdata[i * 2 + 5] == 0xff and getdata[i * 2 + 6] == 0xff:
                setpower[i - 1] = -1
            else:
                setpower[i - 1] = getdata[i * 2 + 5] + (getdata[i * 2 + 6] << 8)
        return setpower

    # Read actual position values from the driver
    def get_actpos(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0xFE
        b[6] = 0x05

        # Length of registers to read
        b[7] = 0x0C

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)
        getdata = self.ser.read(20)


        actpos = [0] * 6
        for i in range(1, 7):
            if getdata[i * 2 + 5] == 0xff and getdata[i * 2 + 6] == 0xff:
                actpos[i - 1] = -1
            else:
                actpos[i - 1] = getdata[i * 2 + 5] + (getdata[i * 2 + 6] << 8)
        return actpos

    # Read actual angle values
    def get_actangle(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0x0A
        b[6] = 0x06

        # Length of registers to read
        b[7] = 0x0C

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(20)

        actangle = [0] * 6
        for i in range(1, 7):
            if getdata[i * 2 + 5] == 0xff and getdata[i * 2 + 6] == 0xff:
                actangle[i - 1] = -1
            else:
                actangle[i - 1] = getdata[i * 2 + 5] + (getdata[i * 2 + 6] << 8)
        return actangle

    # Read actual force values
    def get_actforce(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0x2E
        b[6] = 0x06

        # Length of registers to read
        b[7] = 0x0C

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(20)


        actforce = [0] * 6
        for i in range(1, 7):
            if getdata[i * 2 + 5] == 0xff and getdata[i * 2 + 6] == 0xff:
                actforce[i - 1] = -1
            else:
                actforce[i - 1] = getdata[i * 2 + 5] + (getdata[i * 2 + 6] << 8)

        # Serial reads two-byte unsigned hex values (0–65536). Actual force values are signed (-32768 to 32767),
        # so convert readings >32767 by subtracting 65536 to get the real force value.
        for i in range(len(actforce)):
            if actforce[i] > 32767:
                actforce[i] = actforce[i] - 65536
        return actforce

    # Read current
    def get_current(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0x3A
        b[6] = 0x06

        # Length of registers to read
        b[7] = 0x0C

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(20)

        current = [0] * 6
        for i in range(1, 7):
            if getdata[i * 2 + 5] == 0xff and getdata[i * 2 + 6] == 0xff:
                current[i - 1] = -1
            else:
                current[i - 1] = getdata[i * 2 + 5] + (getdata[i * 2 + 6] << 8)
        return current

    # Read fault information
    def get_error(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0x46
        b[6] = 0x06

        # Length of registers to read
        b[7] = 0x06

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(14)

        error = [0] * 6
        for i in range(1, 7):
            error[i - 1] = getdata[i + 6]
        return error

    # Read status information
    def get_status(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0x4C
        b[6] = 0x06

        # Length of registers to read
        b[7] = 0x06

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
            self.ser.write(putdata)

        getdata = self.ser.read(14)
        status = [0] * 6
        for i in range(1, 7):
            status[i - 1] = getdata[i + 6]
        return status

    # Read temperature information
    def get_temp(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Read operation
        b[4] = 0x11

        # Address
        b[5] = 0x52
        b[6] = 0x06

        # Length of registers to read
        b[7] = 0x06

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(14)

        temp = [0] * 6
        for i in range(1, 7):
            temp[i - 1] = getdata[i + 6]
        return temp

    # Clear errors
    def set_clear_error(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Write operation
        b[4] = 0x12

        # Address
        b[5] = 0xEC
        b[6] = 0x03

        # Data
        b[7] = 0x01

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(9)

    # Save parameters to FLASH
    def set_save_flash(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Write operation
        b[4] = 0x12

        # Address
        b[5] = 0xED
        b[6] = 0x03

        # Data
        b[7] = 0x01

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(18)

    # Force sensor calibration
    def gesture_force_clb(self):
        datanum = 0x04
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Write operation
        b[4] = 0x12

        # Address
        b[5] = 0xF1
        b[6] = 0x03

        # Data
        b[7] = 0x01

        # Checksum
        b[8] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(18)

    # Set default speed on power-up
    def setdefaultspeed(self, speed1, speed2, speed3, speed4, speed5, speed6):
        if speed1 < 0 or speed1 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if speed2 < 0 or speed2 > 1000:
            return
        if speed3 < 0 or speed3 > 1000:
            return
        if speed4 < 0 or speed4 > 1000:
            return
        if speed5 < 0 or speed5 > 1000:
            return
        if speed6 < 0 or speed6 > 1000:
            return

        datanum = 0x0F
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Write operation
        b[4] = 0x12

        # Address
        b[5] = 0x08
        b[6] = 0x04

        # Data
        b[7] = self.data2bytes(speed1)[0]
        b[8] = self.data2bytes(speed1)[1]

        b[9] = self.data2bytes(speed2)[0]
        b[10] = self.data2bytes(speed2)[1]

        b[11] = self.data2bytes(speed3)[0]
        b[12] = self.data2bytes(speed3)[1]

        b[13] = self.data2bytes(speed4)[0]
        b[14] = self.data2bytes(speed4)[1]

        b[15] = self.data2bytes(speed5)[0]
        b[16] = self.data2bytes(speed5)[1]

        b[17] = self.data2bytes(speed6)[0]
        b[18] = self.data2bytes(speed6)[1]

        # Checksum
        b[19] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(9)

    # Set default force thresholds on power-up
    def setdefaultpower(self, power1, power2, power3, power4, power5, power6):
        if power1 < 0 or power1 > 1000:
            print('Value out of valid range: 0 to 1000')
            return
        if power2 < 0 or power2 > 1000:
            return
        if power3 < 0 or power3 > 1000:
            return
        if power4 < 0 or power4 > 1000:
            return
        if power5 < 0 or power5 > 1000:
            return
        if power6 < 0 or power6 > 1000:
            return

        datanum = 0x0F
        b = [0] * (datanum + 5)
        # Header
        b[0] = 0xEB
        b[1] = 0x90

        # hand_id
        b[2] = self.hand_id

        # Number of data items
        b[3] = datanum

        # Write operation
        b[4] = 0x12

        # Address
        b[5] = 0x14
        b[6] = 0x04

        # Data
        b[7] = self.data2bytes(power1)[0]
        b[8] = self.data2bytes(power1)[1]

        b[9] = self.data2bytes(power2)[0]
        b[10] = self.data2bytes(power2)[1]

        b[11] = self.data2bytes(power3)[0]
        b[12] = self.data2bytes(power3)[1]

        b[13] = self.data2bytes(power4)[0]
        b[14] = self.data2bytes(power4)[1]

        b[15] = self.data2bytes(power5)[0]
        b[16] = self.data2bytes(power5)[1]

        b[17] = self.data2bytes(power6)[0]
        b[18] = self.data2bytes(power6)[1]

        # Checksum
        b[19] = self.checknum(b, datanum + 4)

        # Send data to serial port
        putdata = b''

        for i in range(1, datanum + 6):
            putdata = putdata + self.num2str(b[i - 1])
        self.ser.write(putdata)

        getdata = self.ser.read(9)

    def soft_setpos(self, pos1, pos2, pos3, pos4, pos5, pos6):
        value0 = 0
        temp_value = [0, 0, 0, 0, 0, 0]
        is_static = [0, 0, 0, 0, 0, 0]
        static_value = [0, 0, 0, 0, 0, 0]
        pos_value = [pos1, pos2, pos3, pos4, pos5, pos6]
        n = 5
        diffpos = pos1 - self.f1_init_pos
        tic = time.time()
        for ii in range(5):

            actforce = self.get_actforce()
            print('actforce: ', actforce)
            for i, f in enumerate(actforce[0:5]):
                if is_static[i]:
                    continue
                if f > 1000:
                    continue
                if i == 5:  # 大拇指
                    if f > 100:  # 如果手指受力大于100，就维持之前的位置
                        is_static[i] = 1  # 标记为静态手指，手指保持该位置不再动
                        static_value[i] = temp_value[i]  # 上一步的第i个手指位置
                else:
                    if f > 50:  # 如果手指受力大于100，就维持之前的位置
                        is_static[i] = 1  # 标记为静态手指，手指保持该位置不再动
                        static_value[i] = temp_value[i]  # 上一步的第i个手指位置
            temp_value = pos_value.copy()
            for i in range(6):
                if is_static[i]:
                    pos_value[i] = static_value[i]
            pos1 = pos_value[0]  # 小拇指伸直0，弯曲2000
            pos2 = pos_value[1]  # 无名指伸直0，弯曲2000
            pos3 = pos_value[2]  # 中指伸直0，弯曲2000
            pos4 = pos_value[3]  # 食指伸直0，弯曲2000
            pos5 = pos_value[4]  # 大拇指伸直0，弯曲2000
            pos6 = pos_value[5]  # 大拇指转向掌心 2000
            self.setpos(pos1, pos2, pos3, pos4, pos5, pos6)
            toc = time.time()
            print('ii: %d,toc=%f' % (ii, toc - tic))

        return

    def reset(self):
        angle1 = self.f1_init_angle  # Little finger straight 1000, bent 0
        angle2 = self.f2_init_angle  # Ring finger straight 1000, bent 0
        angle3 = self.f3_init_angle  # Middle finger straight 1000, bent 0
        angle4 = self.f4_init_angle  # Index finger straight 1000, bent 0
        angle5 = self.f5_init_angle  # Thumb straight 1000, bent 0
        angle6 = self.f6_init_angle  # Thumb rotates toward the palm 0; 100 means thumb parallel to index
        self.setangle(angle1, angle2, angle3, angle4, angle5, angle6)
        return

    def open_gripper(self, angle=np.array([1000, 1000, 1000, 585, 545, 100]), sleep_time=0.5):
        angle0, angle1, angle2, angle3, angle4, angle5 = angle
        self.setangle(int(angle0), int(angle1), int(angle2), int(angle3), int(angle4), int(angle5))
        time.sleep(sleep_time)

    def close_gripper(self, InspireHandR_type, sleep_time=0.2):
        print("Close gripper")
        close_finger = which_finger_to_close[str(int(InspireHandR_type))]
        angle = self.get_actangle()
        thumb_latitude = 60
        others_latitude = 60
        for latitude in range(1, 20):
            actangle = self.get_actangle()
            for ids, finger in enumerate(close_finger):
                if finger != 0:
                    angle[ids] = max(angle[ids] - others_latitude, finger)    
            angle0, angle1, angle2, angle3, angle4, angle5 = angle
            self.setangle(int(angle0), int(angle1), int(angle2), int(angle3), int(angle4), int(angle5))
        time.sleep(sleep_time)
        