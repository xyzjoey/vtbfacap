import cv2
from .settings import settings


class InputStream:
    def __init__(self, video_path=None):
        self.is_camera = video_path is None

        self.capture = cv2.VideoCapture(0 if self.is_camera else video_path)
        self.capture.set(cv2.CAP_PROP_FPS, settings.fps)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, settings.width)

    def __del__(self):
        self.capture.release()

    def next(self):
        success, frame = self.capture.read()
        return frame if success else None
