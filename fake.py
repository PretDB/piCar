import ctypes
import math


class Mecanum():    # {{{
    def __init__(self):    # {{{
        return
    # }}}

    def move(self, com):    # {{{
        self.carMove(com, 0.2)
        return              # }}}

    def carMove(self, com, speed):  # {{{
        # print('car move ', com, 'at speed = ', speed)
        return                      # }}}
# }}}


class PCA:    # {{{
    # Subaddress did not NotImplemented
    def __init__(self, useSubAddress=False):
        self.channelValue = [0, 0, 0, 0, 0, 0]
        # Sub address
        if useSubAddress:
            print('PCA: pca uses sub address')

        self.setFreq(200)

        return

    def setChannelValue_ratio(self, channel, delay, duty):
        delay_val = delay * 4096
        duty_val = duty * 4096

        on = round(delay_val)
        off = round(delay_val + duty_val - 1)
        self.setChannelValue_raw(channel, on, off)

        return

    def setChannelValue_time_s(self, channel, delay, duty):
        self.setChannelValue_time_us(channel, delay * 1000000, duty * 1000000)

        return

    def setChannelValue_time_ms(self, channel, delay, duty):
        self.setChannelValue_time_us(channel, delay * 1000, duty * 1000)

        return

    def setChannelValue_time_us(self, channel, delay, duty):
        if delay + duty <= self.period * 1000000:
            delay_r = delay / self.period / 1000000
            duty_r = duty / self.period / 1000000

            self.setChannelValue_ratio(channel, delay_r, duty_r)

        return

    # dely and duty are described in count, which means delay + count should
    # less than 4095 ( counter varies from 0 to 4095 ( inclusive ) )
    def setChannelValue_raw(self, channel, on, off):
        self.channelValue[channel] = (on, off)

        return

    # Set frequency ( in Hz ):
    def setFreq(self, freq):
        self.freq = freq
        self.period = 1 / freq

        return

    # Period unit is in s
    def setPeriod(self, period):
        f = 1 / period
        self.setFreq(f)

        return

    def sleep(self, isSleep):
        return

    def reset(self):
        return

# }}}


class MCP:    # {{{
    def __init__(self):    # {{{
        self.INPUT = 1
        self.OUTPUT = 0
        self.HIGH = 1
        self.LOW = 0
        self.ioDirectReg_A = 0x00
        self.ioDirectReg_B = 0x01
        self.iPolarityReg_A = 0x02
        self.iPolarityReg_B = 0x03
        self.gpIntEn_A = 0x04
        self.gpIntEn_B = 0x05
        self.defVal_A = 0x06
        self.defVal_B = 0x07
        self.intCon_A = 0x08
        self.intCon_B = 0x09
        self.ioCon = 0x0A
        self.gpPU_A = 0x0C
        self.gpPU_B = 0x0D
        self.intFlag_A = 0x0E
        self.intFlag_B = 0x0F
        self.intCap_A = 0x10
        self.intCap_B = 0x11
        self.gpio_A = 0x12
        self.gpio_B = 0x13
        self.outLatch_A = 0x14
        self.outLatch_B = 0x15

        self.mode = 0xFFFF
        # output cache, higher 8 bits indicates B port
        self.output = 0x0000    # Default output state is all off
        self.pullUp = 0x0000    # Default pull-up state is all off
        self.invert = 0x0000    # Default input invertion state is not

        self.regs = dict()

        return    # }}}

    def digitalReadAll(self):    # {{{
        raw = self.wordRead(0x12)
        value = int(raw[1]) << 8
        value = value | int(raw[0])
        value = value & 0xFFFF

        # return raw
        return value    # }}}

    def digitalWriteAll(self, value):    # {{{
        value = value & 0xFFFF
        self.wordWrite(0x12, value)

        self.output = value

        return    # }}}

    def digitalRead(self, pin):    # {{{
        if pin > 0 and pin < 17:
            val = self.digitalReadAll()
            ret = (val >> (pin - 1)) & 0x01

            return ret
        else:
            return

# }}}

    # value = 0 or 1 for reset or set
    def digitalWrite(self, pin, value):    # {{{
        if pin > 0 and pin < 17:
            if value == 1:
                val = 0x01 << (pin - 1)
                self.output = self.output | val
            elif value == 0:
                val = ~(1 << (pin - 1))
                self.output = self.output & val

            self.digitalWriteAll(self.output)

        return    # }}}

    def pullupMode(self, state, pin):    # {{{
        pass    # }}}

    def pinModeAll(self, mode):    # {{{
        amode = mode & 0x00FF
        bmode = mode >> 8 & 0x00FF
        self.regWrite(0x00, amode)
        self.regWrite(0x01, bmode)

        self.mode = mode

        pass    # }}}

    def pinMode(self, pin, mode):    # {{{
        self.mode = self.regRead(0x01)
        self.mode = (self.mode << 8) | self.regRead(0x00)

        if pin > 0 and pin < 17:
            if mode == 1:
                mode = 0x01 << (pin - 1)
                self.mode = self.mode | mode
            elif mode == 0:
                mode = ~(1 << (pin - 1))
                self.mode = self.mode & mode

            self.pinModeAll(self.mode)

        pass    # }}}

    def inputInvert(self, invert, pin):    # {{{
        pass    # }}}

    def wordRead(self, addr):    # {{{
        try:
            low = self.regs[addr]
            high = self.regs[addr + 1]
        except(KeyError):
            self.regs[addr] = 0
            self.regs[addr + 1] = 0
            return (0, 0)
        else:
            return (high, low)   # }}}

    def wordWrite(self, addr, data):    # {{{
        low = data & 0x00FF
        high = ((data >> 8) & 0x00FF)
        self.regs[addr] = low
        self.regs[addr + 1] = high
        return    # }}}

    def regRead(self, addr):    # {{{
        try:
            recv = self.regs[addr]
        except(KeyError):
            self.regs[addr] = 0
            return 0
        else:
            return recv    # }}}

    def regWrite(self, addr, value):    # {{{
        self.regs[addr] = value
        return    # }}}
# }}}


class QMC:    # {{{
    def __init__(self):
        self.xoff = 0
        self.yoff = 0
        self.zoff = 0
        self.xgain = 1
        self.ygain = 1
        self.zgain = 1
        return

    def reset(self):
        return

    def set(self):
        return

    def readMag_Raw(self):
        dataRaw = [0, 0, 0, 0, 0, 0]

        return dataRaw

    def readMag(self):
        dataRaw = self.readMag_Raw()
        tmp = [0, 0, 0, 0, 0, 0]
        data = [0, 0, 0]

        tmp[0] = ctypes.c_ubyte(dataRaw[0])
        tmp[2] = ctypes.c_ubyte(dataRaw[2])
        tmp[4] = ctypes.c_ubyte(dataRaw[4])
        tmp[1] = ctypes.c_byte(dataRaw[1])
        tmp[3] = ctypes.c_byte(dataRaw[3])
        tmp[5] = ctypes.c_byte(dataRaw[5])

        # Assembly data
        data[0] = tmp[1].value << 8 | tmp[0].value
        data[1] = tmp[3].value << 8 | tmp[2].value
        data[2] = tmp[5].value << 8 | tmp[4].value

        # Cali
        data[0] = self.xgain * (data[0] + self.xoff)
        data[1] = self.ygain * (data[1] + self.yoff)
        data[2] = self.zgain * (data[2] + self.zoff)

        return data

    def readAngle(self):
        xyz = self.readMag()
        angle = math.atan2(xyz[1], xyz[0]) * 180 / math.pi + 180
        return angle

    def cali(self, write):
        return
# }}}
