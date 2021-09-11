import math

import numpy as np

from ..math_utils import Vectors, Transform2, Ray, Plane
from ..settings import settings, face_settings


class FaceAndIrisLandmarksBase:
    def __init__(self, face_landmarks, left_iris=None, right_iris=None):
        self.face_landmarks: Vectors = face_landmarks  # shape (467, 3)
        self.left_iris_landmarks: Vectors = left_iris  # shape (5, 3)
        self.right_iris_landmarks: Vectors = right_iris  # shape (5, 3)

    def __getattr__(self, name):
        return self.face_landmarks[getattr(face_settings.indices, name)]

    def __setattr__(self, name, value):
        if name in face_settings.indices.__fields__:
            self.face_landmarks[getattr(face_settings.indices, name)] = value
        else:
            super().__setattr__(name, value)


class FaceAndIrisLandmarks(FaceAndIrisLandmarksBase):  # normalized with respect to frame size
    def __init__(self, face_landmarks, left_iris=None, right_iris=None):
        super().__init__(face_landmarks, left_iris, right_iris)
        self._reset_transform_info()

    @property
    def left_iris_center(self):
        return self.left_iris_landmarks[0] if self.left_iris_landmarks is not None else None

    @property
    def right_iris_center(self):
        return self.right_iris_landmarks[0] if self.right_iris_landmarks is not None else None

    def _reset_transform_info(self):
        self._rotation: Vectors = None
        self._origin: Vectors = None
        self._up: Vectors = None
        self._right: Vectors = None
        self._forward: Vectors = None
        self._pitch: float = None
        self._yaw: float = None
        self._roll: float = None

    def _get_bounding_square(self, landmarks, scale):
        min_xy = np.amin(landmarks.no_z(), axis=0)
        max_xy = np.amax(landmarks.no_z(), axis=0)
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
        R = Transform2.rotation(self.up_angle())

        center = eye_contour.center()
        eye_contour_local = (eye_contour - center).transform(R.T)

        box = self._get_bounding_square(eye_contour_local, scale=1.8)
        box = (box.pad_z(1).transform(R) + center).no_z()

        return box

    def get_left_eye_box(self):
        return self._get_eye_box(self.left_eye_contour)

    def get_right_eye_box(self):
        return self._get_eye_box(self.right_eye_contour)

    def set_left_eye_landmarks(self, iris, contour):
        # projection to correct z depth
        Z = Vectors.init([0, 0, 1])
        eye_forward = (self.left_eye_up - self.left_eye_down).cross(self.left_eye_right_corner - self.left_eye_left_corner)
        eye_center = (self.left_eye_up + self.left_eye_down) / 2
        eye_plane = Plane(eye_center, eye_forward)
        eye_ray_from_screen = Ray(iris, Z)
        projected_iris, _ = Vectors.ray_plane_intersect(eye_ray_from_screen, eye_plane)

        self.left_iris_landmarks = projected_iris
        # self.left_eye_contour = contour
        self._reset_transform_info()

    def set_right_eye_landmarks(self, iris, contour):
        # projection to correct z depth
        Z = Vectors.init([0, 0, 1])
        eye_forward = (self.right_eye_up - self.right_eye_down).cross(self.right_eye_right_corner - self.right_eye_left_corner)
        eye_center = (self.right_eye_up + self.right_eye_down) / 2
        eye_plane = Plane(eye_center, eye_forward)
        eye_ray_from_screen = Ray(iris, Z)
        projected_iris, _ = Vectors.ray_plane_intersect(eye_ray_from_screen, eye_plane)

        self.right_iris_landmarks = projected_iris
        # self.right_eye_contour = contour
        self._reset_transform_info()

    def _is_all_visible(self, landmarks):
        """check if within screen"""
        return np.all(landmarks[:,:2] >= 0) and np.all(landmarks[:,0] < settings.width) and np.all(landmarks[:,1] < settings.height)

    def is_left_eye_visible(self):
        return self.yaw() < 0.7 and self._is_all_visible(self.left_eye_contour_2nd_innermost)

    def is_right_eye_visible(self):
        return self.yaw() > -0.7 and self._is_all_visible(self.right_eye_contour_2nd_innermost)

    def origin(self):
        if self._origin is None:
            self._origin = Vectors.init([
                self.left_edge1,
                self.left_edge2,
                self.left_edge3,
                self.right_edge1,
                self.right_edge2,
                self.right_edge3,
            ]).center()
        return self._origin

    # def rotation(self):
    #     """get rotation matrix"""
    #     if self._rotation is None:
    #         self._rotation = Vectors.r_[[self.right()], [-self.up()], [self.forward()]]
    #     return self._rotation

    def up(self):
        if self._up is None:
            self._up = Vectors.init([
                self.left_edge1 - self.left_edge3,
                self.right_edge1 - self.right_edge3,
                self.brows_middle1 - self.eyes_middle2,
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

    def forward(self):  # FIXME affected by mouth open
        if self._forward is None:
            self._forward = self.up().cross(self.right()).normalize()
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
            self._yaw = math.copysign(right.angle(project), -right[2])
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
            self._roll = math.copysign(self.up().angle(up_project), self.right()[1] * -1)
        return self._roll

    def up_angle(self):
        """angle between self up vector and screen up vector"""
        return math.copysign(self.up().no_z().angle(Vectors.init([0, -1])), self.up()[0])
