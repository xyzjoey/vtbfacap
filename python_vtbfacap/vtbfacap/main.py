from .face_data import Live2dShape
from .face_tracking import FaceAndIrisTracking
from .stream import InputFrameStream, OutputStream
from .settings import settings
from .utils import Debug, DebugPlot, FPS, InputKey


def main():
    ifstream = InputFrameStream()  # TODO pass video path
    ostream = OutputStream()
    face_and_iris_tracking = FaceAndIrisTracking()
    blendshape = Live2dShape()  # TODO choose between 2D 3D

    fps = FPS()

    while True:
        if not Debug.paused:
            frame = ifstream.next()

            # TODO terminate if video end
            # if frame is None:
            #     print("end")
            #     break

            face_and_iris_landmarks = face_and_iris_tracking.process(frame)

            print(f"fps: {fps.next()}", end="\r", flush=True)

            if face_and_iris_landmarks is not None:
                blendshape.update(face_and_iris_landmarks)
                ostream.send(blendshape.bytes())
                pass

            # show
            if not settings.hide_window:
                if settings.hide_face:
                    frame[:] = (50, 50, 50)  # fill gray
                Debug.draw_face(face_and_iris_landmarks)
                Debug.show(frame)

        InputKey.wait_key()

        if InputKey.esc():
            break

        if settings.debug_plot:
            if InputKey.p():
                Debug.paused = not Debug.paused

                if Debug.paused:
                    DebugPlot.show()

            if Debug.paused:
                DebugPlot.wait_input()

            DebugPlot.clear()
