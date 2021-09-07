import atexit

import cv2

from .settings import settings


class Debug:
    draw_tasks = []

    @classmethod
    def show(cls, frame):
        for draw_method in cls.draw_tasks:
            draw_method(frame)
        cls.draw_tasks = []
        cv2.imshow("vtbfacap_debug", frame)

    @classmethod
    def draw(cls, draw_method, *args, **kw):
        cls.draw_tasks.append(lambda frame: draw_method(frame, *args, **kw))

    @staticmethod
    def draw_point(point, color=(255, 255, 255)):
        x, y = int(point[0]), int(point[1])
        Debug.draw(cv2.circle, (x, y), 2, color, -1)

    @staticmethod
    def draw_points(points, color=(255, 255, 255), draw_index=False):
        for i, ptr in enumerate(points):
            x, y = int(ptr[0]), int(ptr[1])
            Debug.draw(cv2.circle, (x, y), 2, color, -1)
            if draw_index:
                Debug.draw(cv2.putText, str(i), (x + 2, y + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    @staticmethod
    def draw_box(box, color=(255, 255, 255)):
        if box.shape[0] == 2:  # max & min points
            Debug.draw(cv2.rectangle, box[0].astype(int), box[1].astype(int), color, 2)
        else:  # 4 points
            for i in range(4):
                Debug.draw_line(box[i].astype(int), box[(i+1)%4].astype(int), color)
    
    @staticmethod
    def draw_ray(start, vector, color=(255, 255, 255)):
        Debug.draw(cv2.line, start.vectors2().astype(int), (start + vector).vectors2().astype(int), color, 2)

    @staticmethod
    def draw_line(p1, p2, color=(255, 255, 255)):
        Debug.draw(cv2.line, p1.vectors2().astype(int), p2.vectors2().astype(int), color, 2)

    @staticmethod
    def fill_color(color):
        def draw_method(frame):
            frame[:] = color
        Debug.draw(draw_method)

    @staticmethod
    def draw_face(face_and_iris_landmarks):
        if face_and_iris_landmarks is None:
            return

        multiplier = settings.normalize_multiplier

        # direction
        center = face_and_iris_landmarks.origin() * multiplier
        Debug.draw_ray(center, face_and_iris_landmarks.up() * 100, color=(0, 255, 0))
        Debug.draw_ray(center, face_and_iris_landmarks.right() * 100, color=(255, 0, 0))
        Debug.draw_ray(center, face_and_iris_landmarks.forward() * 100, color=(0, 0, 255))
        # face
        Debug.draw_points(face_and_iris_landmarks.face_landmarks * multiplier, color=(255,255,0))
        # eyes
        if face_and_iris_landmarks.left_iris_landmarks is not None:
            Debug.draw_points(face_and_iris_landmarks.left_eye_contour * multiplier, color=(0,255,0))
            Debug.draw_points(face_and_iris_landmarks.left_iris_landmarks * multiplier, color=(0,0,255))
        if face_and_iris_landmarks.right_iris_landmarks is not None:
            Debug.draw_points(face_and_iris_landmarks.right_eye_contour * multiplier, color=(0,255,0))
            Debug.draw_points(face_and_iris_landmarks.right_iris_landmarks * multiplier, color=(0,0,255))

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
