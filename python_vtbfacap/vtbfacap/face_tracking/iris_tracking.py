import cv2 as cv
import numpy as np
# import tensorflow as tf

from ..math_utils import Vectors


class IrisTrackingV2:
    # TODO differentiate blink and looking down

    def _binarize_image(self, frame, threshold):
        kernel = np.ones((3, 3), np.uint8)
        new_frame = cv.bilateralFilter(frame, 10, 15, 15)
        new_frame = cv.erode(new_frame, kernel, iterations=3)
        new_frame = cv.equalizeHist(new_frame)
        new_frame = cv.threshold(new_frame, threshold, 255, cv.THRESH_BINARY)[1]
        new_frame = cv.dilate(new_frame, kernel, iterations=3)
        return new_frame

    def _get_2nd_biggest_contour(self, contours):
        contours = sorted(contours, key=cv.contourArea)
        return contours[-2] if len(contours) >= 2 else None

    def _get_contour_center(self, contour):
        moments = cv.moments(contour)
        if moments["m00"] != 0 and moments["m00"] != 0:
            iris_x = moments["m10"] / moments["m00"]
            iris_y = moments["m01"] / moments["m00"]
            return Vectors.init([iris_x, iris_y])

        return None

    def _find_iris_contour(self, binary_frame):
        binary_frame = binary_frame.astype(np.uint8)
        padded_frame = np.pad(binary_frame, 1, constant_values=1)  # pad to avoid contour touching edge
        contours, _ = cv.findContours(padded_frame, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)[-2:]
        iris_contour = self._get_2nd_biggest_contour(contours)  # 1st biggest contour is frame edge

        if iris_contour is not None:
            iris_contour -= (1, 1)  # cancel pad border

        return iris_contour

    def _draw_contour_edge(self, shape, contour):
        white_frame = np.full(shape[:2], 0, dtype=np.uint8)
        return cv.drawContours(white_frame, [contour], -1, (255), thickness=0)

    def _get_iris_vertices(self, iris_frame, iris_center: Vectors):
        # find intersect with x position
        iris_x = int(iris_center[0])
        intersect = np.copy(iris_frame)
        intersect[:,:iris_x] *= 0
        intersect[:,iris_x+1:] *= 0
        intersect_coordinates = list(zip(*(np.nonzero(intersect.T))))

        if len(intersect_coordinates) == 0:
            return iris_center, iris_center

        top = min(intersect_coordinates, key=lambda p: p[1])
        bottom = max(intersect_coordinates, key=lambda p: p[1])

        eye_up = Vectors.init(top)
        eye_down = Vectors.init(bottom)
        return eye_up, eye_down

    def _find_iris(self, frame, threshold=50):
        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        binary_frame = self._binarize_image(gray_frame, threshold)
        iris_contour = self._find_iris_contour(binary_frame)

        if iris_contour is None:
            return None, None

        iris_frame = self._draw_contour_edge(frame.shape, iris_contour)
        return iris_frame, iris_contour

    def process(self, frame):
        iris_frame, iris_contour = self._find_iris(frame)
        iris_center = self._get_contour_center(iris_contour) if iris_contour is not None else None

        if iris_center is None:
            return None

        iris_up, iris_down = self._get_iris_vertices(iris_frame, iris_center)

        if iris_up is None or iris_down is None:
            return None

        return Vectors.init([iris_center, iris_up, iris_down], dtype=float)


# # input: right eye frame with no rotation
# # using mediapipe model
# # https://github.com/Kazuhito00/iris-detection-using-py-mediapipe
# class IrisTracking:
#     def __init__(
#         self,
#         model_path=settings.iris_model_path,
#         num_threads=1,
#     ):
#         self._interpreter = tf.lite.Interpreter(model_path=model_path, num_threads=num_threads)
#         self._interpreter.allocate_tensors()
#         self._input_details = self._interpreter.get_input_details()
#         self._output_details = self._interpreter.get_output_details()

#     def process(self, image):
#         input_shape = self._input_details[0]["shape"]

#         # preprocess
#         img = cv.cvtColor(image, cv.COLOR_BGR2RGB)
#         img = img / 255.0
#         img_resized = tf.image.resize(img, [input_shape[1], input_shape[2]], method="bicubic", preserve_aspect_ratio=False)
#         img_input = img_resized.numpy()
#         img_input = (img_input - 0.5) / 0.5

#         reshape_img = img_input.reshape(1, input_shape[1], input_shape[2], input_shape[3])
#         tensor = tf.convert_to_tensor(reshape_img, dtype=tf.float32)

#         # compute
#         input_details_tensor_index = self._input_details[0]["index"]
#         self._interpreter.set_tensor(input_details_tensor_index, tensor)
#         self._interpreter.invoke()

#         # get result
#         output_details_tensor_index0 = self._output_details[0]["index"]
#         output_details_tensor_index1 = self._output_details[1]["index"]
#         eye_contour = self._interpreter.get_tensor(output_details_tensor_index0)
#         iris = self._interpreter.get_tensor(output_details_tensor_index1)

#         # postprocess
#         eye_contour = np.reshape(np.squeeze(eye_contour), (-1, 3))
#         iris = np.reshape(np.squeeze(iris), (-1, 3))
#         # normalize  # Q: what to do with z?
#         eye_contour[:, 0] /= input_shape[1]
#         eye_contour[:, 1] /= input_shape[2]
#         iris[:, 0] /= input_shape[1]
#         iris[:, 1] /= input_shape[2]

#         return eye_contour.view(Vectors), iris.view(Vectors)

#     def get_input_shape(self):
#         input_shape = self._input_details[0]["shape"]
#         return [input_shape[1], input_shape[2]]  # 64 x 64 model input
