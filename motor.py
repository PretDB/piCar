import wiringpi
import pca

class Motor:
    def __init__( self, pcaInstance, pwmChannel, invPin ):
        self.pwmChannel = pwmChannel
        self.invPin = invPin
        self.pca = pcaInstance

        return

    # speed is described in ratio
    def rotate( self, inverse, speed ):
        if not inverse:
            wiringpi.digitalWrite( self.invPin, wiringpi.LOW )
        else:
            wiringpi.digitalWrite( self.invPin, wiringpi.HIGH )

        self.pca.setChannelValue_ratio( self.pwmChannel, 0, speed )
        return

    def stop( self ):
        self.rotate( False, 0 )

        return
