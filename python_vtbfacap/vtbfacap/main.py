from .face_data import Live2dShape
from .face_tracking import FaceAndIrisTracking
from .frame import InputFrame
from .stream import OutputStream
from .settings import settings
from .utils import Debug, FPS, InputKey


def main():
    iframe = InputFrame()  # TODO pass video path
    ostream = OutputStream()
    face_and_iris_tracking = FaceAndIrisTracking()
    blendshape = Live2dShape()  # TODO choose between 2D 3D

    fps = FPS()

    while True:
        frame = iframe.next()

        if frame is None:
            print("end")
            break
        
        face_and_iris_landmarks = face_and_iris_tracking.process(frame)

        print(f"fps: {fps.next()}", end="\r", flush=True)

        if face_and_iris_landmarks is not None:
            blendshape.update(face_and_iris_landmarks)
            ostream.send(blendshape.bytes())
            pass

        # show
        if not settings.hide_window:
            if settings.hide_face:
                Debug.fill_color(frame, (50, 50, 50))
            Debug.draw_face(frame, face_and_iris_landmarks)
            Debug.show(frame)

        if InputKey.wait_esc():
            break
