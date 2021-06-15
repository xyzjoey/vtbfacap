import os

from pydantic import BaseSettings

this_file_dir = os.path.dirname(os.path.realpath(__file__))


class Settings(BaseSettings):
    width: int = 640
    height: int = 480
    fps: int = 30

    # landmarks info https://github.com/tensorflow/tfjs-models/blob/master/facemesh/mesh_map.jpg
    face_landmark_num: int = 467
    left_eye_landmark_indices = [133, 173, 157, 158, 159, 160, 161, 246, 163, 144, 145, 153, 154, 155]
    right_eye_landmark_indices = [362, 398, 384, 385, 386, 387, 388, 466, 390, 373, 374, 380, 381, 382]

    iris_model_path: str = f"{this_file_dir}/../data/iris_landmark.tflite"  # copied from mediapipe

    @property
    def normalize_factor(self):
        return float(max(self.width, self.height))

settings = Settings()
