import wiringpi


class MCP:
    def __init__(self, channel, addr):    # {{{
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

        self.readAddr = 0x41 | (addr << 1)
        self.writeAddr = 0x40 | (addr << 1)
        self.channel = channel

        self.mode = 0xFFFF
        # output cache, higher 8 bits indicates B port
        self.output = 0x0000    # Default output state is all off
        self.pullUp = 0x0000    # Default pull-up state is all off
        self.invert = 0x0000    # Default input invertion state is not

        # wiringpi.wiringPiSetupGpio()
        wiringpi.wiringPiSPISetup(self.channel, 500000)

        return    # }}}

    def digitalReadAll(self):    # {{{
        raw = self.wordRead(0x12)
        value = int(raw[1]) << 8
        value = value | int(raw[0])
        value = value & 0xFFFF

        return raw    # }}}

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
        send = bytes([self.readAddr, addr, 0x00, 0x00])
        recv = wiringpi.wiringPiSPIDataRW(self.channel, send)

        return (recv[1][2], recv[1][3])    # }}}

    def wordWrite(self, addr, data):    # {{{
        send = bytes([self.writeAddr, addr,
                      (data & 0x00FF), ((data >> 8) & 0x00FF)])
        wiringpi.wiringPiSPIDataRW(self.channel, send)
        return    # }}}

    def regRead(self, addr):    # {{{
        send = bytes([self.readAddr, addr, 0x00])
        recv = wiringpi.wiringPiSPIDataRW(self.channel, send)
        return recv[1][2]    # }}}

    def regWrite(self, addr, value):    # {{{
        send = bytes([self.writeAddr, addr, value])
        wiringpi.wiringPiSPIDataRW(self.channel, send)
        return    # }}}
