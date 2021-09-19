import atexit

import cv2
import matplotlib.pyplot as matplot
import numpy as np

from .settings import settings


class Debug:
    frame = None
    draw_tasks = []
    paused = False

    @staticmethod
    def _close():
        cv2.destroyAllWindows()

    @classmethod
    def apply_draw(cls, frame):
        if frame.dtype == np.bool:  # do not use 'is' for checking np.dtype
            frame = frame.astype(np.uint8) * 255
        if frame.ndim < 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        for draw_method in cls.draw_tasks:
            draw_method(frame)
        cls.draw_tasks = []

        if cls.frame is None:
            cls.frame = frame
        else:
            # pad & concat
            width_diff = frame.shape[1] - cls.frame.shape[1]
            if width_diff > 0:
                cls.frame = np.pad(cls.frame, ((0, 0), (0, width_diff), (0, 0)), constant_values=255)
            elif width_diff < 0:
                frame = np.pad(frame, ((0, 0), (0, -width_diff), (0, 0)), constant_values=255)
            cls.frame = np.concatenate((cls.frame, frame), axis=0)

    @classmethod
    def show(cls):
        if cls.frame is not None:
            cv2.imshow("vtbfacap", cls.frame)
        cls.draw_tasks = []
        cls.frame = None

    @classmethod
    def push_draw_task(cls, draw_method, *args, **kw):
        cls.draw_tasks.append(lambda frame: draw_method(frame, *args, **kw))

    @staticmethod
    def _check_point(frame, point):
        x, y = point
        if x < 0 or y < 0 or x >= frame.shape[1] or y >= frame.shape[0]:
            return False
        return True

    @staticmethod
    def draw_point(point, color=(255, 255, 255)):
        x, y = int(point[0]), int(point[1])
        Debug.push_draw_task(lambda frame: Debug._check_point(frame, (x, y)) and cv2.circle(frame, (x, y), 2, color, -1))

    @staticmethod
    def draw_points(points, color=(255, 255, 255), draw_index=False):
        for i, ptr in enumerate(points):
            Debug.draw_point(ptr, color)
            # x, y = int(ptr[0]), int(ptr[1])
            # Debug.push_draw_task(cv2.circle, (x, y), 2, color, -1)
            # if draw_index:
            #     Debug.push_draw_task(cv2.putText, str(i), (x + 2, y + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    @staticmethod
    def draw_keypoints(keypoints, color=(255, 255, 255)):
        Debug.push_draw_task(lambda frame: cv2.drawKeypoints(frame, keypoints, frame, color, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS))

    @staticmethod
    def draw_contours(contours, color=(255, 255, 255), thickness=None):
        Debug.push_draw_task(cv2.drawContours, contours, -1, color, thickness)

    @staticmethod
    def draw_box(box, color=(255, 255, 255)):
        if box.shape[0] == 2:  # max & min points
            Debug.push_draw_task(cv2.rectangle, box[0].astype(int), box[1].astype(int), color, 2)
        else:  # 4 points
            for i in range(4):
                Debug.draw_line(box[i].astype(int), box[(i + 1) % 4].astype(int), color)

    @staticmethod
    def draw_ray(start, vector, color=(255, 255, 255)):
        Debug.push_draw_task(cv2.arrowedLine, start.no_z().astype(int), (start + vector).no_z().astype(int), color, 2)

    @staticmethod
    def draw_line(p1, p2, color=(255, 255, 255)):
        Debug.push_draw_task(cv2.line, p1.no_z().astype(int), p2.no_z().astype(int), color, 2)

    @staticmethod
    def draw_face(face_and_iris_landmarks):
        if face_and_iris_landmarks is None:
            return

        m = settings.normalize_multiplier

        # direction
        center = face_and_iris_landmarks.origin() * m
        Debug.draw_ray(center, face_and_iris_landmarks.up() * 100, color=(0, 255, 0))
        Debug.draw_ray(center, face_and_iris_landmarks.right() * 100, color=(255, 0, 0))
        Debug.draw_ray(center, face_and_iris_landmarks.forward() * 100, color=(0, 0, 255))
        # face
        Debug.draw_points(face_and_iris_landmarks.face_landmarks * m, color=(255, 255, 0))
        # eyes
        if face_and_iris_landmarks.left_iris_landmarks is not None:
            Debug.draw_points(face_and_iris_landmarks.left_iris_landmarks * m, color=(0, 0, 255))
        if face_and_iris_landmarks.right_iris_landmarks is not None:
            Debug.draw_points(face_and_iris_landmarks.right_iris_landmarks * m, color=(0, 0, 255))


atexit.register(Debug._close)


class DebugPlot:
    plot_tasks = []

    @classmethod
    def _convert_color(cls, color):
        return tuple(v / 255 for v in color)

    @classmethod
    def add_plot_task(cls, get_method, *args, **kw):
        if settings.debug_plot:
            cls.plot_tasks.append((get_method, *args, kw))

    @classmethod
    def plot_points(cls, pts, color=(255, 255, 255)):
        cls.add_plot_task(lambda axis: axis.scatter, pts.x, pts.y, pts.z, color=cls._convert_color(color))

    @classmethod
    def show(cls):
        fig = matplot.figure()
        axis = fig.add_subplot(111, projection="3d")
        # axis.axis('equal')

        for get_method, *args, kw in cls.plot_tasks:
            plot_method = get_method(axis)
            plot_method(*args, **kw)
        cls.plot_tasks = []

        fig.show()

    @classmethod
    def wait_input(cls):
        matplot.pause(0.01)

    @classmethod
    def clear(cls):
        cls.plot_tasks = []


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
    last_key = None

    @classmethod
    def wait_key(cls):
        cls.last_key = cv2.waitKey(1)

    @classmethod
    def esc(cls):
        return cls.last_key == 27  # ESC

    @classmethod
    def p(cls):
        return cls.last_key == ord("p")
