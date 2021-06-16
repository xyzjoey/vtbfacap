import os
from typing import List

from pydantic import BaseSettings

this_file_dir = os.path.dirname(os.path.realpath(__file__))


class Settings(BaseSettings):
    width: int = 640
    height: int = 480
    fps: int = 30

    iris_model_path: str = f"{this_file_dir}/../data/iris_landmark.tflite"  # copied from mediapipe

    # debug
    hide_window: bool = False
    hide_face: bool = True

    @property
    def normalize_factor(self):
        return float(max(self.width, self.height))

settings = Settings()


class FaceSettings(BaseSettings):
    # landmarks info https://github.com/tensorflow/tfjs-models/blob/master/facemesh/mesh_map.jpg
    class LandmarkIndices(BaseSettings):
        left_eye_contour: List[int] = [
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
        left_eye_contour_2nd_innermost: List[int] = [
            130, 25, 110, 24, 23, 22, 26, 112, 243,
            247, 30, 29, 27, 28, 56, 190,
        ]
        right_eye_contour: List[int] = [
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
        right_eye_contour_2nd_innermost: List[int] = [
            359, 255, 339, 254, 253, 252, 256, 341, 463,
            467, 260, 259, 257, 258, 286, 414,
        ]

        eyes_middle: int = 6
        brows_middle1: int = 8
        brows_middle2: int = 9

        chin: int = 152

        left_edge1: int = 127
        left_edge2: int = 234
        left_edge3: int = 93
        right_edge1: int = 356
        right_edge2: int = 454
        right_edge3: int = 323

    indices = LandmarkIndices()
    landmark_num: int = 468

face_settings = FaceSettings()
