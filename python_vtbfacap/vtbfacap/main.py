from .face_tracking import FaceAndIrisTracking
from .input_stream import InputStream
from .settings import settings
from .utils import Debug, FPS, InputKey


def main():
    istream = InputStream()  # TODO pass video path
    face_and_iris_tracking = FaceAndIrisTracking()
    fps = FPS()

    while True:
        frame = istream.next()

        if frame is None:
            print("end")
            break
        
        face_and_iris_landmarks = face_and_iris_tracking.process(frame)

        print(f"fps: {fps.next()}", end="\r", flush=True)

        if face_and_iris_landmarks is not None:
            # TODO blendshape.update(face_and_iris_landmarks)
            # TODO ostream.send(blendshape.bytes())
            pass

        # show
        if not settings.hide_window:
            if settings.hide_face:
                Debug.fill_color(frame, (50, 50, 50))
            Debug.draw_face(frame, face_and_iris_landmarks)
            Debug.show(frame)

        if InputKey.wait_esc():
            break
