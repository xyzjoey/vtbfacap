import cv2
import mediapipe as mp

from ..face_data import FaceAndIrisLandmarks
from ..math_utils import Vectors
from ..settings import settings, face_settings


class FaceTracking:
    def __init__(
        self,
        # max_num_faces=1,  # assume always 1 face
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
    ):
        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb_frame)

        if result.multi_face_landmarks is None:
            return None

        normalized_landmarks = Vectors.empty(shape=(face_settings.landmark_num, 3), dtype=float)
        width_multiplier = float(settings.width) / settings.normalize_multiplier
        height_multiplier = float(settings.height) / settings.normalize_multiplier

        for landmarks in result.multi_face_landmarks:
            for i in range(face_settings.landmark_num):
                # fmt: off
                normalized_landmarks[i] = [landmarks.landmark[i].x * width_multiplier,
                                           landmarks.landmark[i].y * height_multiplier,
                                           landmarks.landmark[i].z]
                # fmt: on
            break  # assume 1 face

        return FaceAndIrisLandmarks(face_landmarks=normalized_landmarks)
