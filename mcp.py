import wiringpi

class MCP:
    def __init__( self, add, ss ):
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

        self.address = add
        self.ss =  ss
        self.mode = 0xFFFF      # Default IO mode is all input
        self.output = 0x0000    # Default output state is all off
        self.pullUp = 0x0000    # Default pull-up state is all off
        self.invert = 0x0000    # Default input invertion state is not

        pass
    def digitalRead( self, pin ):
        pass

    def digitalWrite( self, pin, value ):
        pass

    def pullupMode( self, state, pin ):
        pass

    def pinMode( self, state, pin ):
        pass

    def inputInvert( self, invert, pin):
        pass

    def wordWrite( self, value ):
        pass

    def byteWrite( self, value ):
        pass

    def byteRead( self, value ):
        pass
