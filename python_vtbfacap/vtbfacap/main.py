from .face_tracking import FaceAndIrisTracking
from .input_stream import InputStream
from .settings import settings
from .utils import Debug, FPS, Input


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

            # if settings.debug:
            Debug.draw_points(frame, face_and_iris_landmarks.left_iris[:,:2] * settings.normalize_factor, color=(0,0,255))
            Debug.draw_points(frame, face_and_iris_landmarks.left_eye_contour[:,:2] * settings.normalize_factor, color=(0,255,0))

            Debug.draw_points(frame, face_and_iris_landmarks.right_iris[:,:2] * settings.normalize_factor, color=(0,0,255))
            Debug.draw_points(frame, face_and_iris_landmarks.right_eye_contour[:,:2] * settings.normalize_factor, color=(0,255,0))

            Debug.draw_points(frame, face_and_iris_landmarks.face_landmarks[:,:2] * settings.normalize_factor, color=(255,0,0))
        
        Debug.show(frame)

        if Input.wait_esc():
            break
