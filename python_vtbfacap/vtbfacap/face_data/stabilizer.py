import cv2
import numpy as np


class Stabilizer:
    def __init__(
        self,
        # state_num=2,
        # measure_num=1,
        cov_process=0.01,
        cov_measure=0.1
    ):
        # assert state_num == 4 or state_num == 2

        self.state_num = 2
        self.measure_num = 1
        self.cov_process = cov_process
        self.cov_measure = cov_measure

        self.filter = cv2.KalmanFilter(self.state_num, self.measure_num, 0)

        self.state = np.zeros((self.state_num, 1), dtype=np.float32)
        self.measurement = np.array((self.measure_num, 1), np.float32)
        self.prediction = np.zeros((self.state_num, 1), np.float32)
        
        if self.measure_num == 1:
            self.filter.transitionMatrix = np.array([[1, 1],
                                                     [0, 1]], np.float32)
            self.filter.measurementMatrix = np.array([[1, 1]], np.float32)
            self.filter.processNoiseCov = np.array([[1, 0],
                                                    [0, 1]], np.float32) * self.cov_process
            self.filter.measurementNoiseCov = np.array(
                [[1]], np.float32) * self.cov_measure

    def correct(self, value):
        self.prediction = self.filter.predict()

        if self.measure_num == 1:
            self.measurement = np.array([[np.float32(value)]])

        self.filter.correct(self.measurement)
        self.state = self.filter.statePost
        return self.state[0, 0]
