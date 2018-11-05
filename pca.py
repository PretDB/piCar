import wiringpi
import time

class PCA:
    # Subaddress did not NotImplemented
    def __init__( self, useSubAddress = False ):
        self.modeReg1_address = 0x00
        self.modeReg2_address = 0x01
        self.pwmReg_addressBase = 0x06
        self.prescalerReg_address = 0xFE
        self.testModeReg_address = 0xFF

        self.address = 0x40
        self.all_led_address = 0x70
        self.reset_address = 0x00
        self.handler = wiringpi.wiringPiI2CSetup( self.address )
        self.all_led_handler = wiringpi.wiringPiI2CSetup( self.all_led_address )
        self.reset_handler = wiringpi.wiringPiI2CSetup( self.reset_address )
        # Sub address
        if useSubAddress:
            self.sub1_address = 0x71
            self.sub2_address = 0x72
            self.sub3_address = 0x74
            self.sub1_handler = wiringpi.wiringPiI2CSetup( self.sub1_address )
            self.sub2_handler = wiringpi.wiringPiI2CSetup( self.sub2_address )
            self.sub3_handler = wiringpi.wiringPiI2CSetup( self.sub3_address )

        self.setFreq( 200 )

        return

    def setChannelValue_ratio( self, channel, delay, duty ):
        delay_val = delay * 4096 - 1
        duty_val = duty * 4096 - 1

        self.setChannelValue_raw( channel, round( delay_val ), round( duty_val ) )

        return

    def setChannelValue_time_s( self, channel, delay, duty ):
        self.setChannelValue_time_us( channel, delay * 1000000, duty * 1000000 )

        return

    def setChannelValue_time_ms( self, channel, delay, duty ):
        self.setChannelValue_time_ms( channel, delay * 1000, duty * 1000 )

        return

    def setChannelValue_time_us( self, channel, delay, duty ):
        if delay + duty <= self.period:
            delay_r = delay / self.period
            duty_r = duty / self.period

            self.setChannelValue_ratio( channel, delay_r, duty_r )

        return

    # dely and duty are described in count, which means delay + count should
    # less than 4095 ( counter varies from 0 to 4095 ( inclusive ) )
    def setChannelValue_raw( self, channel, on, off ):
        on_l = on & 0x00FF
        on_h = ( on & 0xFF00 ) >> 8
        off_l = ( off + on ) & 0x00FF
        off_h = ( ( off + on ) & 0xFF00 ) >> 8

        base = self.pwmReg_addressBase + channel * 4

        wiringpi.wiringPiI2CWriteReg8( self.handler, base + 0, on_l )
        wiringpi.wiringPiI2CWriteReg8( self.handler, base + 1, on_h )
        wiringpi.wiringPiI2CWriteReg8( self.handler, base + 2, off_l )
        wiringpi.wiringPiI2CWriteReg8( self.handler, base + 3, off_h )

        return

    # Set frequency ( in Hz ):
    def setFreq( self, freq ):
        value = round( 25000000 / 4096 / freq ) - 1

        self.sleep( True )
        wiringpi.wiringPiI2CWriteReg8( self.handler, self.prescalerReg_address, value )
        self.sleep( False )
        time.sleep( 1 )

        self.freq = freq
        self.period = 1 / freq

        return

    # Period unit is in s
    def setPeriod( self, period ):
        f = 1 / period
        self.setFreq( f )

        return

    def sleep( self, isSleep ):
        current = wiringpi.wiringPiI2CReadReg8( self.handler, 0x00 )

        if isSleep:
            wiringpi.wiringPiI2CWriteReg8( self.handler, self.modeReg1_address, current | 0x10 )
            pass
        else:
            wiringpi.wiringPiI2CWriteReg8( self.handler, self.modeReg1_address, current & 0xEF )
            pass

    def reset( self ):
        wiringpi.wiringPiI2CWrite( self.reset_handler, 0x06 )
        time.sleep( 1 )

        return
