import math

import cv2
import numpy as np

from ..face_data import FaceAndIrisLandmarks
from .face_tracking import FaceTracking
from .iris_tracking import IrisTrackingV2
from ..math_utils import Vectors, Transform2
from ..settings import settings


class FaceAndIrisTracking:
    def __init__(self):
        self.face_tracking = FaceTracking()
        self.iris_tracking = IrisTrackingV2()

    def _get_bounding_box(self, landmarks: Vectors):
        min_xy = np.amin(landmarks.no_z(), axis=0)
        max_xy = np.amax(landmarks.no_z(), axis=0)
        # fmt: off
        return Vectors.init([min_xy,  # left top
                            [min_xy[0], max_xy[1]],  # left bottom
                            max_xy,  # right bottom
                            [max_xy[0], min_xy[1]]])  # right top
        # fmt: on

    def _get_rotated_box(self, landmarks: Vectors, box_up_vector: Vectors):
        # rotation between box up vector and screen up vector
        rotation_angle = math.copysign(box_up_vector.no_z().angle(Vectors.init([0, -1])), box_up_vector[0])
        R = Transform2.rotation(rotation_angle)

        center = landmarks.center()
        landmarks_local = (landmarks - center).transform(R.T)

        box = self._get_bounding_box(landmarks_local)
        box = (box.pad_z(1).transform(R) + center).no_z()

        return box

    def _crop_frame(self, frame, box):
        width = (box[3] - box[0]).length()
        height = (box[1] - box[0]).length()

        src_box = box.astype("float32")
        # fmt: off
        dst_box = Vectors.init([[0, 0],
                                [0, height - 1],
                                [width - 1, height - 1],
                                [width - 1, 0]], dtype="float32")
        # fmt: on

        M = cv2.getPerspectiveTransform(src_box, dst_box)
        return cv2.warpPerspective(frame, M, (int(width), int(height)))

    def _mask_frame(self, frame, contour: Vectors):
        """make area outside contour white"""
        mask = np.full(frame.shape, 255, dtype=frame.dtype)
        cv2.fillPoly(mask, [contour.astype(int)], (0, 0, 0))
        return cv2.bitwise_or(frame, mask)

    def _valid_points(self, frame_shape, landmarks):
        """check if points within frame"""
        frame_height = frame_shape[0]
        frame_width = frame_shape[1]
        m = settings.normalize_multiplier
        return np.all(landmarks[:, :2] >= 0) and np.all(landmarks[:, 0] < frame_width / m) and np.all(landmarks[:, 1] < frame_height / m)

    def process(self, frame) -> FaceAndIrisLandmarks:
        face_landmarks = self.face_tracking.process(frame)

        if face_landmarks is None:
            return None

        is_left_eye_visible = face_landmarks.yaw() < 0.7 and self._valid_points(frame.shape, face_landmarks.left_eye_contour_2nd_innermost)
        is_right_eye_visible = face_landmarks.yaw() > -0.7 and self._valid_points(frame.shape, face_landmarks.right_eye_contour_2nd_innermost)

        if is_left_eye_visible:
            iris_landmarks = self.process_eye_v2(frame, face_landmarks, left=True)
            if iris_landmarks is not None:
                face_landmarks.set_left_eye_landmarks(iris_landmarks)

        if is_right_eye_visible:
            iris_landmarks = self.process_eye_v2(frame, face_landmarks, left=False)
            if iris_landmarks is not None:
                face_landmarks.set_right_eye_landmarks(iris_landmarks)

        return face_landmarks

    def process_eye_v2(self, frame, face_landmarks, left):
        eye_contour = getattr(face_landmarks, "left_eye_contour_2nd_innermost" if left else "right_eye_contour_2nd_innermost")

        m = settings.normalize_multiplier
        box = self._get_rotated_box(eye_contour, face_landmarks.up())

        eye_frame = self._mask_frame(frame, eye_contour.no_z() * m)
        eye_frame = self._crop_frame(eye_frame, box * m)

        landmarks = self.iris_tracking.process(eye_frame)

        if landmarks is not None:
            # transform back onto face
            global_o = box[0]
            global_x = box[3] - box[0]
            global_y = box[1] - box[0]
            X = (landmarks[:, 0] / eye_frame.shape[1]).outer(global_x)
            Y = (landmarks[:, 1] / eye_frame.shape[0]).outer(global_y)
            landmarks = X + Y + global_o

            landmarks = landmarks.pad_z(1)

        return landmarks
