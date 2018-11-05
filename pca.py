import wiringpi
import time

class PCA:
    def __init__( self, useSubAddress = False ):

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


    def reset( self ):
        wiringpi.wiringPiI2CWrite( self.reset_handler, 0x06 )
        time.sleep( 1 )

        return
