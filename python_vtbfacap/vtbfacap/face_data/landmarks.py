import math

import numpy as np
from numpy.core.defchararray import center
from pydantic.dataclasses import dataclass

from ..math_utils import Vectors, Transform2
from ..settings import settings, face_settings


class FaceAndIrisLandmarks:  # normalized with respect to frame size
    def __init__(self, face_landmarks, left_iris=None, right_iris=None):
        self.face_landmarks: Vectors = face_landmarks  # shape (467, 3)
        self.left_iris_landmarks: Vectors = left_iris  # shape (5, 3)
        self.right_iris_landmarks: Vectors = right_iris  # shape (5, 3)

        self._reset_direction_values()

    def __getattr__(self, name):
        return self.face_landmarks[getattr(face_settings.indices, name)]

    def __setattr__(self, name, value):
        if name in face_settings.indices.__fields__:
            self.face_landmarks[getattr(face_settings.indices, name)] = value
            self._reset_direction_values()
        else:
            super().__setattr__(name, value)

    def _reset_direction_values(self):
        self._up = None
        self._right = None
        self._forward = None
        self._pitch = None
        self._yaw = None
        self._roll = None

    def _get_bounding_square(self, landmarks, scale):
        min_xy = np.amin(landmarks.vectors2(), axis=0)
        max_xy = np.amax(landmarks.vectors2(), axis=0)
        box = Vectors.init([
            min_xy,
            [min_xy[0], max_xy[1]],
            max_xy,
            [max_xy[0], min_xy[1]],
        ])

        center = (min_xy + max_xy) / 2
        xy_size = max_xy - min_xy
        square_size = np.max(xy_size)

        # scale & extend one side to square
        box -= center
        box *= (square_size / xy_size) * scale
        box += center 

        return box

    def _get_eye_box(self, eye_contour):
        R = Transform2.rotation(self.angle_y())

        center = eye_contour.center()
        eye_contour_local = (eye_contour - center).transform(R.T)

        box = self._get_bounding_square(eye_contour_local, scale=1.8)
        box = (box.vectors3().transform(R) + center).vectors2()

        return box

    def get_left_eye_box(self):
        return self._get_eye_box(self.left_eye_contour)

    def get_right_eye_box(self):
        return self._get_eye_box(self.right_eye_contour)

    def set_left_eye_landmarks(self, iris, contour):
        self.left_iris_landmarks = iris
        self.left_eye_contour = contour

    def set_right_eye_landmarks(self, iris, contour):
        self.right_iris_landmarks = iris
        self.right_eye_contour = contour

    def _is_all_visible(self, landmarks):
        return np.all(landmarks[:,:2] >= 0) and np.all(landmarks[:,0] < settings.width) and np.all(landmarks[:,1] < settings.height)

    def is_left_eye_visible(self):
        return self._is_all_visible(self.left_eye_contour_2nd_innermost) and self.yaw() > -0.7

    def is_right_eye_visible(self):
        return self._is_all_visible(self.right_eye_contour_2nd_innermost) and self.yaw() < 0.7

    def up(self):
        if self._up is None:
            self._up = Vectors.init([
                self.eyes_middle - self.chin,
                self.brows_middle1 - self.chin,
                self.brows_middle2 - self.chin,
            ]).mean(axis=0).normalize()
        return self._up

    def right(self):
        if self._right is None:
            self._right = Vectors.init([
                self.right_edge1 - self.left_edge1,
                self.right_edge2 - self.left_edge2,
                self.right_edge3 - self.left_edge3,
            ]).mean(axis=0).normalize()
        return self._right

    def forward(self):
        if self._forward is None:
            self._forward = self.right().cross(self.up()).normalize()
        return self._forward

    def pitch(self):
        if self._pitch is None:
            forward = self.forward()
            project = Vectors.init([forward[0], 0, forward[2]])
            self._pitch = math.copysign(forward.angle(project), -forward[1])
        return self._pitch

    def yaw(self):
        if self._yaw is None:
            right = self.right()
            project = Vectors.init([right[0], right[1], 0])
            self._yaw = math.copysign(right.angle(project), right[2])
        return self._yaw

    def roll(self):
        if self._roll is None:
            forward = self.forward()
            if forward[1] == 0:
                up_project = Vectors.init([0, 1, 0])
            else:
                forward_project = Vectors.init([forward[0], 0, forward[2]])
                right_project = forward_project.cross(forward) if forward[1] > 0 else forward.cross(forward_project)
                up_project = forward.cross(right_project).normalize()
            self._roll = math.copysign(self.up().angle(up_project), self.right()[1])
        return self._roll

    def angle_y(self):
        return math.copysign(self.up().vectors2().angle(Vectors.init([0, -1])), self.up()[0])
