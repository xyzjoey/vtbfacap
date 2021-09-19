import math

from ..math_utils import Vectors, Ray, Plane
from ..settings import face_settings


class FaceAndIrisLandmarksBase:
    def __init__(self, face_landmarks, left_iris=None, right_iris=None):
        self.face_landmarks: Vectors = face_landmarks  # shape (467, 3)
        self.left_iris_landmarks: Vectors = left_iris  # shape (3, 3)
        self.right_iris_landmarks: Vectors = right_iris  # shape (3, 3)

    def __getattr__(self, name):
        return self.face_landmarks[getattr(face_settings.indices, name)]

    def __setattr__(self, name, value):
        if name in face_settings.indices.__fields__:
            self.face_landmarks[getattr(face_settings.indices, name)] = value
        else:
            super().__setattr__(name, value)


class FaceAndIrisLandmarks(FaceAndIrisLandmarksBase):  # normalized with respect to frame size
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self._reset_transform_info()

    @property
    def left_iris_center(self):
        return self.left_iris_landmarks[0] if self.left_iris_landmarks is not None else None

    @property
    def left_iris_up(self):
        return self.left_iris_landmarks[1] if self.left_iris_landmarks is not None else None

    @property
    def left_iris_down(self):
        return self.left_iris_landmarks[2] if self.left_iris_landmarks is not None else None

    @property
    def right_iris_center(self):
        return self.right_iris_landmarks[0] if self.right_iris_landmarks is not None else None

    @property
    def right_iris_up(self):
        return self.right_iris_landmarks[1] if self.right_iris_landmarks is not None else None

    @property
    def right_iris_down(self):
        return self.right_iris_landmarks[2] if self.right_iris_landmarks is not None else None

    def _reset_transform_info(self):
        self._rotation: Vectors = None
        self._origin: Vectors = None
        self._up: Vectors = None
        self._right: Vectors = None
        self._forward: Vectors = None
        self._pitch: float = None
        self._yaw: float = None
        self._roll: float = None

    def get_left_eye_box(self):
        return self._get_eye_box(self.left_eye_contour)

    def get_right_eye_box(self):
        return self._get_eye_box(self.right_eye_contour)

    def set_left_eye_landmarks(self, iris_landmarks):
        # projection to correct z depth
        Z = Vectors.init([0, 0, 1])
        eye_forward = (self.left_eye_up - self.left_eye_down).cross(self.left_eye_right_corner - self.left_eye_left_corner)
        eye_center = (self.left_eye_up + self.left_eye_down) / 2
        eye_plane = Plane(eye_center, eye_forward)
        iris_ray_from_screen = Ray(iris_landmarks, Z)

        projected_iris_landmarks, _ = Vectors.ray_plane_intersect(iris_ray_from_screen, eye_plane)

        self.left_iris_landmarks = projected_iris_landmarks
        self._reset_transform_info()

    def set_right_eye_landmarks(self, iris_landmarks):
        # projection to correct z depth
        Z = Vectors.init([0, 0, 1])
        eye_forward = (self.right_eye_up - self.right_eye_down).cross(self.right_eye_right_corner - self.right_eye_left_corner)
        eye_center = (self.right_eye_up + self.right_eye_down) / 2
        eye_plane = Plane(eye_center, eye_forward)
        iris_ray_from_screen = Ray(iris_landmarks, Z)

        projected_iris_landmarks, _ = Vectors.ray_plane_intersect(iris_ray_from_screen, eye_plane)

        self.right_iris_landmarks = projected_iris_landmarks
        self._reset_transform_info()

    def origin(self):
        if self._origin is None:
            # fmt: off
            self._origin = Vectors.init([self.left_edge1,
                                         self.left_edge2,
                                         self.left_edge3,
                                         self.right_edge1,
                                         self.right_edge2,
                                         self.right_edge3]).center()
            # fmt: on
        return self._origin

    # def rotation(self):
    #     """get rotation matrix"""
    #     if self._rotation is None:
    #         self._rotation = Vectors.r_[[self.right()], [-self.up()], [self.forward()]]
    #     return self._rotation

    def up(self):
        if self._up is None:
            # fmt: off
            nose_middle = Vectors.init([
                self.nose_right,
                self.nose_left,
                self.nose_tip
            ]).mean(axis=0)
            self._up = (self.eyes_middle2 - nose_middle).normalize()
            # fmt: on
        return self._up

    def right(self):
        if self._right is None:
            # fmt: off
            self._right = Vectors.init([
                self.right_eye_right_corner - self.left_eye_left_corner,
                self.nose_right - self.nose_left,
            ]).mean(axis=0).normalize()
            # fmt: on
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
