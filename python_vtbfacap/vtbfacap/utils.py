import atexit

import cv2

from .settings import settings


class Debug:
    @staticmethod
    def show(frame):
        cv2.imshow("vtbfacap_debug", frame)

    @staticmethod
    def draw_points(frame, points, color=(255, 255, 255), put_indices=False):
        for i, row in enumerate(points):
            x, y = int(row[0]), int(row[1])
            cv2.circle(frame, (x, y), 2, color, -1)
            if put_indices:
                cv2.putText(frame, str(i), (x + 2, y + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    @classmethod
    def draw_box(cls, frame, box, color=(255, 255, 255)):
        if box.shape[0] == 2:  # max & min points
            cv2.rectangle(frame, box[0].astype(int), box[1].astype(int), color, 2)
        else:  # 4 points
            for i in range(4):
                cls.draw_line(frame, box[i].astype(int), box[(i+1)%4].astype(int), color)
    
    @staticmethod
    def draw_ray(frame, start, vector, color=(255, 255, 255)):
        cv2.line(frame, start.vectors2().astype(int), (start + vector).vectors2().astype(int), color, 2)

    @staticmethod
    def draw_line(frame, p1, p2, color=(255, 255, 255)):
        cv2.line(frame, p1.vectors2().astype(int), p2.vectors2().astype(int), color, 2)

    @staticmethod
    def fill_color(frame, color):
        frame[:] = color

    @staticmethod
    def draw_face(frame, face_and_iris_landmarks):
        if face_and_iris_landmarks is None:
            return

        factor = settings.normalize_factor

        # direction
        center = face_and_iris_landmarks.face_landmarks.center() * factor
        up = face_and_iris_landmarks.up()
        right = face_and_iris_landmarks.right()
        forward = face_and_iris_landmarks.forward()
        Debug.draw_ray(frame, center, up * 100, color=(0, 255, 0))
        Debug.draw_ray(frame, center, right * 100, color=(255, 0, 0))
        Debug.draw_ray(frame, center, forward * 100, color=(0, 0, 255))
        # face
        Debug.draw_points(frame, face_and_iris_landmarks.face_landmarks * factor, color=(255,255,0))
        # eyes
        if face_and_iris_landmarks.left_iris_landmarks is not None:
            Debug.draw_points(frame, face_and_iris_landmarks.left_eye_contour * factor, color=(0,255,0))
            Debug.draw_points(frame, face_and_iris_landmarks.left_iris_landmarks * factor, color=(0,0,255))
        if face_and_iris_landmarks.right_iris_landmarks is not None:
            Debug.draw_points(frame, face_and_iris_landmarks.right_eye_contour * factor, color=(0,255,0))
            Debug.draw_points(frame, face_and_iris_landmarks.right_iris_landmarks * factor, color=(0,0,255))

        print(f"roll: {face_and_iris_landmarks.roll()}")

    @staticmethod
    def _close():
        cv2.destroyAllWindows()

atexit.register(Debug._close)


class FPS:
    def __init__(self):
        self.prev_tick = cv2.getTickCount()

    def next(self):
        curr_tick = cv2.getTickCount()
        dt = (curr_tick - self.prev_tick) / cv2.getTickFrequency()
        fps = 1.0 / dt

        self.prev_tick = curr_tick

        return round(fps, 2)


class InputKey:
    @staticmethod
    def wait_esc():
        key = cv2.waitKey(1)
        return key == 27  # ESC
