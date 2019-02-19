import numpy


class Kalman():
    def __init__(self, q=0, r=0.1, n_dim_obs=1, n_dim_state=1):
        self.q = q * numpy.eye(n_dim_state)
        self.r = r * numpy.eye(n_dim_state)

        self.state = numpy.zeros((n_dim_state, n_dim_state), numpy.float)

        self.conv = numpy.eye(n_dim_state)

        self.state_ = numpy.zeros((n_dim_state, n_dim_state), numpy.float)
        self.conv_ = numpy.eye(n_dim_state)

        self.transformMatrix = numpy.eye(n_dim_state)

        self.n_dim_state = n_dim_state
        self.n_dim_obs = n_dim_obs

        pass

    def update(self, measure):
        self.timeUpdate()
        self.measureUpdate(measure)
        return [self.state, self.conv]
        pass

    def timeUpdate(self):
        stateEst_ = self.transformMatrix * self.state
        cov_ = self.transformMatrix * self.conv * \
            numpy.transpose(self.transformMatrix) + self.q

        self.conv_ = cov_
        self.state_ = stateEst_

        return [stateEst_, cov_]
        pass

    def measureUpdate(self, measure):
        K = self.conv_ * numpy.linalg.inv(self.conv + self.r)
        stateEst = self.state_ + K * (measure - self.state)
        conv = (numpy.eye(self.n_dim_state) - K) * self.conv_

        self.state = stateEst
        self.conv = conv

        return [stateEst, conv]
        pass
