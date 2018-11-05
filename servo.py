class Servo:
    def __init__( self, pca, channel, maxAngle = 180, minTime = 0.5, maxTime = 1.5 ):
        self.pca = pca
        self.channel = channel

        self.maxAngle = maxAngle
        self.minTime = minTime
        self.maxTime = maxTime
        pca.setChannelValue_time_ms( channel, 0, minTime )
        self.angle = 0

        return

    def setAngle( self, angle ):
        if angle <= self.maxAngle:
            time = angle / self.maxAngle * ( self.maxTime - self.minTime )
            self.pca.setChannelValue_time_ms( self.channel, 0, time )

        return
