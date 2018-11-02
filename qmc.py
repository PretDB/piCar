import wiringpi
import time
import ctypes


class QMC:
    def __init__(self):
        self.address = 0x0d
        self.handler = wiringpi.wiringPiI2CSetup( self.address )

        self.reset()

    def reset( self ):
        self.writeReg( 0x0A, 0x80 )
        time.sleep( 0.1 )
        self.set()

    def set( self ):
        self.writeReg( 0x0B, 0x01 )
        self.writeReg( 0x09, 0x1D )

    def writeReg( self, addr, val ):
        return wiringpi.wiringPiI2CWriteReg8( self.handler, addr, val )

    def readReg( self, addr ):
        raw = wiringpi.wiringPiI2CReadReg8( self.handler, addr )
        return raw

    def readMag_Raw( self ):
        dataRaw = [0, 0, 0, 0, 0, 0]
        ready_raw = self.readReg( 0x06 )

        if ready_raw & 0x01 == 0x01:
            for i in range( 6 ):
                dataRaw[i] = self.readReg( i )

        return dataRaw

    def readMag( self ):
        dataRaw = self.readMag_Raw()
        tmp = [0, 0, 0, 0, 0, 0]
        data = [ 0, 0, 0]

        tmp[0] = ctypes.c_ubyte( dataRaw[0] )
        tmp[2] = ctypes.c_ubyte( dataRaw[2] )
        tmp[4] = ctypes.c_ubyte( dataRaw[4] )
        tmp[1] = ctypes.c_byte( dataRaw[1] )
        tmp[3] = ctypes.c_byte( dataRaw[3] )
        tmp[5] = ctypes.c_byte( dataRaw[5] )

        data[0] = tmp[1].value << 8 | tmp[0].value
        data[1] = tmp[3].value << 8 | tmp[2].value
        data[2] = tmp[5].value << 8 | tmp[4].value

        return data
