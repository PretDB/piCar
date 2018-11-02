import wiringpi
import ctypes


class QMC:
    def __inti__(self):
        self.address = 0x0d
        self.handler = wiringpi.wiringPiI2CSetup( self.address )

    def writeReg( self, addr, val ):
        return wiringpi.wiringPiI2CWriteReg8( self.handler, addr, val )

    def readReg( self, addr ):
        raw = wiringpi.wiringPiI2CReadReg8( self.handler, addr )
        return raw

    def readMag_Raw( self ):
        dataRaw = (0, 0, 0, 0, 0, 0)
        ready_raw = self.readReg( 0x06 )

        if ready_raw & 0x01 == 0x01:
            for i in range( 6 ):
                dataRaw[i] = self.readReg( i )

        return dataRaw
