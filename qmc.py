import wiringpi
import time
import ctypes
import math


class QMC:
    def __init__(self, readCali):
        self.address = 0x0d
        self.handler = wiringpi.wiringPiI2CSetup( self.address )

        self.xoff = 0
        self.yoff = 0
        self.zoff = 0
        self.xgain = 1
        self.ygain = 1
        self.zgain = 1
        if readCali == True:
            try:
                f = open('cali.conf', 'r')
                self.xoff = float( f.readline() )
                self.yoff = float( f.readline() )
                self.zoff = float( f.readline() )
                self.xgain = float( f.readline() )
                self.ygain = float( f.readline() )
                self.zgain = float( f.readline() )
            except FileNotFoundError:
                f = open('cali.conf', 'w')
                f.flush()
                f.close()

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

        # Assembly data
        data[0] = tmp[1].value << 8 | tmp[0].value
        data[1] = tmp[3].value << 8 | tmp[2].value
        data[2] = tmp[5].value << 8 | tmp[4].value

        # Cali
        data[0] = self.xgain * ( data[0] + self.xoff )
        data[1] = self.ygain * ( data[1] + self.yoff )
        data[2] = self.zgain * ( data[2] + self.zoff )

        return data

    def readAngle( self ):
        xyz = self.readMag()
        angle = math.atan2(xyz[1], xyz[0]) * 180 / math.pi + 180
        return angle

    def cali( self, write ):
        x = list()
        y = list()
        z = list()

        for i in range(2000):
            xx, yy, zz = self.readMag()
            x.append(xx)
            y.append(yy)
            z.append(zz)
            time.sleep(0.005)

        xmax = max( x )
        ymax = max( y )
        zmax = max( z )
        xmin = min( x )
        ymin = min( y )
        zmin = min( z )
        xoff = - ( ( xmax - xmin ) / 2 )
        yoff = - ( ( ymax - ymin ) / 2 )
        zoff = - ( ( zmax - zmin ) / 2 )

        xgain = 1
        ygain = ( xmax - xmin ) / ( ymax - ymin )
        zgain = ( xmax - xmin ) / ( zmax - zmin )

        if write == True:
            f = open( 'cali.conf', 'w' )
            f.write( str( xoff ) + '\n')
            f.write( str( yoff ) + '\n')
            f.write( str( zoff ) + '\n')
            f.write( str( xgain ) + '\n' )
            f.write( str( ygain ) + '\n' )
            f.write( str( zgain ) + '\n' )
            f.close()

        self.xoff = xoff
        self.yoff = yoff
        self.zoff = zoff
        self.xgain = xgain
        self.ygain = ygain
        self.zgain = zgain

        return xoff, xgain, yoff, ygain, zoff, zgain
