import copy

from .face_tracking import FaceTracking
from .iris_tracking import IrisTracking
from ..settings import settings


class FaceAndIrisTracking:
    def __init__(self):
        self.face_tracking = FaceTracking()
        self.iris_tracking = IrisTracking()

    def _crop_frame(self, frame, box):
        height, width, _ = frame.shape

        x1 = int(max(box[0,0], 0))
        y1 = int(max(box[0,1], 0))
        x2 = int(min(box[1,0], width))
        y2 = int(min(box[1,1], height))

        return copy.deepcopy(frame[y1:y2,x1:x2])

    def process(self, frame):
        face_landmarks = self.face_tracking.process(frame)

        if face_landmarks is None:
            return None

        # FIXME remove rotation and flip right eye, skip eye if not completely visible
        left_eye_landmarks = self.process_iris(frame, face_landmarks.get_left_eye_box() * settings.normalize_factor)
        right_eye_landmarks = self.process_iris(frame, face_landmarks.get_right_eye_box() * settings.normalize_factor)
        face_landmarks.set_left_eye_landmarks(left_eye_landmarks)
        face_landmarks.set_right_eye_landmarks(right_eye_landmarks)

        return face_landmarks

    def process_iris(self, frame, eye_box):
        eye_frame = self._crop_frame(frame, eye_box)
        
        # normalized for eye_frame
        eye_landmarks = self.iris_tracking.process(eye_frame)

        # normailzed for frame
        eye_landmarks.contour[:,:2] = (eye_landmarks.contour[:,:2] * eye_frame.shape[0] + eye_box[0]) / settings.normalize_factor
        eye_landmarks.iris[:,:2] = (eye_landmarks.iris[:,:2] * eye_frame.shape[0] + eye_box[0]) / settings.normalize_factor

        return eye_landmarks
