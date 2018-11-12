import wiringpi
import pca

class Motor:
    def __init__( self, pcaInstance, pwmChannel, mcpInstance, invPin ):
        self.pwmChannel = pwmChannel
        self.invPin = invPin
        self.pca = pcaInstance
        self.mcp = mcpInstance

        self.mcp.pinMode(self.invPin, 0)

        return

    # speed is described in ratio
    # inverse = True or 1 for inverse
    def rotate(self, inverse, speed):
        if not inverse:
            self.mcp.digitalWrite(self.invPin, 0)
            self.pca.setChannelValue_ratio(self.pwmChannel, 0, 1 - speed)
        else:
            self.mcp.digitalWrite(self.invPin, 1)
            self.pca.setChannelValue_ratio(self.pwmChannel, 0, speed)

        return

    def stop(self):
        self.rotate(False, 0)

        return
