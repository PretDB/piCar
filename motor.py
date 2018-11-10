import wiringpi
import pca

class Motor:
    def __init__( self, pcaInstance, pwmChannel, invPin ):
        self.pwmChannel = pwmChannel
        self.invPin = invPin
        self.pca = pcaInstance

        return

    # speed is described in ratio
    # inverse = True or 1 for inverse
    def rotate(self, inverse, speed):
        if not inverse:
            wiringpi.digitalWrite(self.invPin, wiringpi.LOW)
            self.pca.setChannelValue_ratio(self.pwmChannel, 0, 1 - speed)
        else:
            wiringpi.digitalWrite(self.invPin, wiringpi.HIGH)
            self.pca.setChannelValue_ratio(self.pwmChannel, 0, speed)

        return

    def stop(self):
        self.rotate(False, 0)

        return
