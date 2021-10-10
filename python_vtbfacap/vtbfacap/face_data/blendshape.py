from dataclasses import dataclass

from .stabilizer import Stabilizer
from .landmarks import FaceAndIrisLandmarks
from ..math_utils import Mathf
from ..settings import face_settings


@dataclass
class Live2dShape:
    yaw: float = 0.5
    pitch: float = 0.5
    roll: float = 0.5
    mouth_open: float = 0
    mouth_form: float = 0.5
    left_eye_open: float = 1
    right_eye_open: float = 1
    iris_x: float = 0.5
    iris_y: float = 0.5

    def __post_init__(self):
        """create stabilizers"""
        for field_name in self.__dataclass_fields__:
            stabilize_param = getattr(face_settings.blendshape_adjust, f"stablize_{field_name}", [])
            if stabilize_param is not None:
                setattr(self, f"_{field_name}_stabilizer", Stabilizer(*stabilize_param))

    def __setattr__(self, name, value):
        """adjust value before assign (map range & stabilize)"""
        if name in self.__dataclass_fields__:
            if value is None:
                return

            minmax_range = getattr(face_settings.blendshape_adjust, f"{name}_range", None)
            stabilizer = getattr(self, f"_{name}_stabilizer", None)

            if minmax_range is not None:
                value = Mathf.map(value, *minmax_range)
            if stabilizer is not None:
                value = stabilizer.correct(value)

        super().__setattr__(name, value)

    def update(self, landmarks: FaceAndIrisLandmarks):
        face_width = (landmarks.right_edge3 - landmarks.left_edge3).length()
        mouth_width = (landmarks.mouth_corner_left - landmarks.mouth_corner_right).length()

        self.yaw = landmarks.yaw() + 0.5  # shift center to 0.5
        self.pitch = landmarks.pitch() + 0.5
        self.roll = landmarks.roll() + 0.5
        self.mouth_open = (landmarks.upper_lip_inner_edge_samples - landmarks.lower_lip_inner_edge_samples).center().length() / mouth_width
        self.mouth_form = mouth_width / face_width
        self.left_eye_open, self.right_eye_open = self.compute_eye_open(landmarks)
        self.iris_x, self.iris_y = self.compute_iris(landmarks)

    def compute_eye_open(self, landmarks):
        left_open = None
        right_open = None

        use_left = self.yaw < 0.6 and landmarks.left_iris_landmarks is not None
        use_right = self.yaw > 0.4 and landmarks.right_iris_landmarks is not None

        right = landmarks.right()
        up = landmarks.up()
        reference = (landmarks.eyes_middle1 - landmarks.eyes_middle2).project(right, up).length()

        if use_left:
            left_open = (landmarks.left_iris_up - landmarks.left_iris_down).project(right, up).length()
            left_open = left_open / reference

        if use_right:
            right_open = (landmarks.right_iris_up - landmarks.right_iris_down).project(right, up).length()
            right_open = right_open / reference

        if left_open is None:
            return right_open, right_open
        elif right_open is None:
            return left_open, left_open
        return left_open, right_open

    def compute_iris(self, landmarks):
        right = landmarks.right()
        up = landmarks.up()
        left_iris = landmarks.left_iris_center
        right_iris = landmarks.right_iris_center

        is_left_valid = False
        is_right_valid = False

        def valid(value):
            return value is not None and value >= 0 and value <= 1

        # left x y
        if left_iris is not None:
            X1 = (left_iris - landmarks.left_eye_right_corner).project(right)
            X2 = (landmarks.left_eye_left_corner - landmarks.left_eye_right_corner).project(right)
            Y1 = (left_iris - landmarks.left_eye_down_reference).project(up)
            Y2 = (landmarks.eyes_middle1 - landmarks.left_eye_down_reference).project(up)
            left_x = X1.length() / X2.length()
            left_y = Y1.length() / Y2.length()
            is_left_valid = valid(left_x) and valid(left_y)

        # right x y
        if right_iris is not None:
            X1 = (right_iris - landmarks.right_eye_right_corner).project(right)
            X2 = (landmarks.right_eye_left_corner - landmarks.right_eye_right_corner).project(right)
            Y1 = (right_iris - landmarks.right_eye_down_reference).project(up)
            Y2 = (landmarks.eyes_middle1 - landmarks.right_eye_down_reference).project(up)
            right_x = X1.length() / X2.length()
            right_y = Y1.length() / Y2.length()
            is_right_valid = valid(right_x) and valid(right_y)

        # final x y
        if is_left_valid and is_right_valid:
            iris_x = (left_x + right_x) / 2
            iris_y = (left_y + right_y) / 2
        elif is_left_valid:
            iris_x, iris_y = left_x, left_y
        elif is_right_valid:
            iris_x, iris_y = right_x, right_y
        else:
            iris_x, iris_y = None, None

        return iris_x, iris_y

    def bytes(self):
        msg = " ".join([f"{getattr(self, name):.4f}" for name in self.__dataclass_fields__])
        return msg.encode("ascii")
