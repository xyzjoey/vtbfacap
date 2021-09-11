import os
from typing import List, Tuple

from pydantic import BaseSettings
import numpy

this_file_dir = os.path.dirname(os.path.realpath(__file__))


class Settings(BaseSettings):
    # input
    width: int = 640
    height: int = 480
    fps: int = 30

    iris_model_path: str = f"{this_file_dir}/../data/iris_landmark.tflite"  # copied from mediapipe

    # computation
    normalize_multiplier: float = None  # init in __post_init__

    # UDP
    host: str = "127.0.0.1"
    port: int = 5066

    # debug
    debug_plot: bool = False
    hide_window: bool = False
    hide_face: bool = True
    numpy_float_format: str = "{:.5f}"

    def __init__(self, **kw):
        super().__init__(**kw)
        self.normalize_multiplier = float(max(self.width, self.height))
        self.__post_init__()

    def __post_init__(self):
        numpy.set_printoptions(formatter={"float_kind": self.numpy_float_format.format})


# fmt: off
class FaceSettings(BaseSettings):
    class BlendshapeAdjust(BaseSettings):
        # map range to 0, 1
        mouth_form_range: Tuple[float, float] = (0.3, 0.45)
        left_eye_open_range: Tuple[float, float] = (0.7, 1.3)
        right_eye_open_range: Tuple[float, float] = (0.7, 1.3)
        # should stablize or not (default True)
        stablize_mouth_open: bool = False

    # landmarks info https://github.com/tensorflow/tfjs-models/blob/master/facemesh/mesh_map.jpg
    # left right from avatar's view
    class LandmarkIndices(BaseSettings):
        # mouth
        upper_lip_center: int = 13
        lower_lip_center: int = 14
        mouth_corner_right: int = 61
        mouth_corner_left: int = 291
        upper_lip_outter_edge_samples: List[int] = [39, 0, 269]
        upper_lip_inner_edge_samples: List[int] = [81, 13, 311]
        lower_lip_outter_edge_samples: List[int] = [181, 17, 405]
        lower_lip_inner_edge_samples: List[int] = [178, 14, 402]

        # eye
        left_eye_up: int = 386
        left_eye_down: int = 374
        left_eye_left_corner: int = 466
        left_eye_right_corner: int = 362
        right_eye_up: int = 159
        right_eye_down: int = 145
        right_eye_right_corner: int = 33
        right_eye_left_corner: int = 133
        right_eye_contour: List[int] = [
            33, 7, 163, 144, 145, 153, 154, 155, 133,
            246, 161, 160, 159, 158, 157, 173,
            130, 25, 110, 24, 23, 22, 26, 112, 243,
            247, 30, 29, 27, 28, 56, 190,
            226, 31, 228, 229, 230, 231, 232, 233, 244,
            113, 223, 224, 223, 222, 221, 189,
            25, 124, 46, 53, 52, 65,
            143, 111, 117, 118, 119, 120, 121, 128, 245,
            156, 70, 63, 105, 66, 107, 55, 193
        ]
        right_eye_contour_2nd_innermost: List[int] = [
            130, 25, 110, 24, 23, 22, 26, 112, 243,
            247, 30, 29, 27, 28, 56, 190,
        ]
        left_eye_contour: List[int] = [
            263, 249, 390, 373, 374, 380, 381, 382, 362,
            466, 388, 387, 386, 385, 384, 398,
            359, 255, 339, 254, 253, 252, 256, 341, 463,
            467, 260, 259, 257, 258, 286, 414,
            446, 261, 448, 449, 450, 451, 452, 453, 464,
            342, 445, 444, 443, 442, 441, 413,
            265, 353, 276, 263, 282, 295,
            372, 340, 346, 347, 348, 349, 350, 357, 465,
            383, 300, 293, 334, 296, 336, 285, 417
        ]
        left_eye_contour_2nd_innermost: List[int] = [
            359, 255, 339, 254, 253, 252, 256, 341, 463,
            467, 260, 259, 257, 258, 286, 414,
        ]

        # nose bridge
        eyes_middle1: int = 168
        eyes_middle2: int = 6
        brows_middle1: int = 8
        brows_middle2: int = 9

        chin: int = 152

        # edge near ear
        right_edge1: int = 127
        right_edge2: int = 234
        right_edge3: int = 93
        left_edge1: int = 356
        left_edge2: int = 454
        left_edge3: int = 323

    blendshape_adjust = BlendshapeAdjust()
    indices = LandmarkIndices()
    landmark_num: int = 468
# fmt: on

settings = Settings()
face_settings = FaceSettings()
