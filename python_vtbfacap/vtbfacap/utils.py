import atexit
import cv2


class Debug:
    @staticmethod
    def show(frame):
        cv2.imshow("vtbfacap_debug", frame)

    @staticmethod
    def draw_points(frame, matrix, color=(100, 100, 0)):
        for row in matrix:
            cv2.circle(frame, (int(row[0]), int(row[1])), 2, color, -1)

    @staticmethod
    def draw_rectangle(frame, box):
        cv2.rectangle(frame, (int(box[0,0]), int(box[0,1])), (int(box[1,0]), int(box[1,1])), (255, 0, 0), 2)

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


class Input:
    @staticmethod
    def wait_esc():
        key = cv2.waitKey(1)
        return key == 27  # ESC
