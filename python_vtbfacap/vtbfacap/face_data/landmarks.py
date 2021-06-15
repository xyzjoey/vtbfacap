import numpy as np
from numpy.core.defchararray import center
from pydantic.dataclasses import dataclass

from ..settings import settings

class NumpyConfig:
    arbitrary_types_allowed = True


@dataclass
class Landmark:
    x: float
    y: float
    z: float
    # visibility
    # presence


@dataclass(config=NumpyConfig)
class IrisLandmarks:
    contour: np.ndarray  # shape (71, 3)
    iris: np.ndarray  # shape (5, 3)

#     @property
#     def contour(self):
#         pass

#     @property
#     def center(self):
#         pass


@dataclass(config=NumpyConfig)
class FaceAndIrisLandmarks:  # normalized
    face_landmarks: np.ndarray  # shape (467, 3)
    
    left_iris: np.ndarray = None  # shape (5, 3)
    left_eye_contour = None

    right_iris: np.ndarray = None  # shape (5, 3)
    right_eye_contour = None

    def _get_bounding_square(self, landmarks, scale):
        min_xyz = np.amin(landmarks, axis=0)
        max_xyz = np.amax(landmarks, axis=0)
        box = np.vstack((min_xyz, max_xyz))

        # scale & extend length to cube
        center = np.mean(box, axis=0)
        box = (box - center) * scale

        lengths = box[1] - box[0]
        max_length = np.max(lengths)
        box = (box * max_length) / lengths

        box += center 

        return box[:,:2]  # TODO remove z earlier

    def get_left_eye_box(self, scale=3):
        return self._get_bounding_square(self.face_landmarks[settings.left_eye_landmark_indices], scale=scale)

    def get_right_eye_box(self, scale=3):
        return self._get_bounding_square(self.face_landmarks[settings.right_eye_landmark_indices], scale=scale)

    def set_left_eye_landmarks(self, landmarks: IrisLandmarks):
        self.left_iris = landmarks.iris
        self.left_eye_contour = landmarks.contour

    def set_right_eye_landmarks(self, landmarks: IrisLandmarks):
        self.right_iris = landmarks.iris
        self.right_eye_contour = landmarks.contour
