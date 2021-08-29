import cv2

from .face_tracking import FaceTracking
from .iris_tracking import IrisTracking
from ..math_utils import Vectors, Transform2
from ..settings import settings


class FaceAndIrisTracking:
    def __init__(self):
        self.face_tracking = FaceTracking()
        self.iris_tracking = IrisTracking()

    def _crop_frame(self, frame, box):
        width = (box[3] - box[0]).length()
        height = (box[1] - box[0]).length()

        src_box = box.astype("float32")
        dst_box = Vectors.init([
            [0, 0],
            [0, height - 1],
            [width - 1, height - 1],
            [width - 1, 0]
        ], dtype="float32")

        M = cv2.getPerspectiveTransform(src_box, dst_box)
        return cv2.warpPerspective(frame, M, (int(width), int(height)))

    def process(self, frame):
        face_landmarks = self.face_tracking.process(frame)

        if face_landmarks is None:
            return None

        # get eye landmarks
        angle = face_landmarks.up_angle()
        if face_landmarks.is_right_eye_visible():
            right_contour, right_iris = self.process_eye(frame, face_landmarks.get_right_eye_box(), angle, flip=False)
            face_landmarks.set_right_eye_landmarks(iris=right_iris, contour=right_contour)
        if face_landmarks.is_left_eye_visible():
            left_contour, left_iris = self.process_eye(frame, face_landmarks.get_left_eye_box(), angle, flip=True)
            face_landmarks.set_left_eye_landmarks(iris=left_iris, contour=left_contour)

        return face_landmarks

    def process_eye(self, frame, eye_box, angle, flip):
        eye_frame = self._crop_frame(frame, eye_box * settings.normalize_factor)  # always square
        eye_frame_size = eye_frame.shape[0]

        if flip:
            eye_frame = cv2.flip(eye_frame, 1)

        contour, iris = self.iris_tracking.process(eye_frame)

        if flip:
            M = Transform2.flip()
            center = Vectors.init([0.5, 0.5, 0])
            contour = contour.transform(M, origin=center)
            iris = iris.transform(M, origin=center)

        # normalize
        contour = contour * eye_frame_size / settings.normalize_factor
        iris = iris * eye_frame_size / settings.normalize_factor

        # transform back to position of face
        R = Transform2.rotation(angle)
        contour = contour.transform(R) + eye_box[0].vectors3(z=0)
        iris = iris.transform(R) + eye_box[0].vectors3(z=0)

        return contour, iris
