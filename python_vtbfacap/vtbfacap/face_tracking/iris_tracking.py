# src: https://github.com/Kazuhito00/iris-detection-using-py-mediapipe

import cv2 as cv
import numpy as np
import tensorflow as tf

from ..math_utils import Vectors
from ..settings import settings


# for right eye with no rotation
# TODO use mediapipe when iris supported
class IrisTracking:
    def __init__(
        self,
        model_path=settings.iris_model_path,
        num_threads=1,
    ):
        self._interpreter = tf.lite.Interpreter(model_path=model_path,
                                                num_threads=num_threads)
        self._interpreter.allocate_tensors()
        self._input_details = self._interpreter.get_input_details()
        self._output_details = self._interpreter.get_output_details()

    def process(self,image):
        input_shape = self._input_details[0]['shape']

        # preprocess
        img = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        img = img / 255.0
        img_resized = tf.image.resize(img, [input_shape[1], input_shape[2]],
                                      method='bicubic',
                                      preserve_aspect_ratio=False)
        img_input = img_resized.numpy()
        img_input = (img_input - 0.5) / 0.5

        reshape_img = img_input.reshape(1, input_shape[1], input_shape[2],
                                        input_shape[3])
        tensor = tf.convert_to_tensor(reshape_img, dtype=tf.float32)

        # compute
        input_details_tensor_index = self._input_details[0]['index']
        self._interpreter.set_tensor(input_details_tensor_index, tensor)
        self._interpreter.invoke()

        # get result
        output_details_tensor_index0 = self._output_details[0]['index']
        output_details_tensor_index1 = self._output_details[1]['index']
        eye_contour = self._interpreter.get_tensor(
            output_details_tensor_index0)
        iris = self._interpreter.get_tensor(output_details_tensor_index1)

        # postprocess
        eye_contour = np.reshape(np.squeeze(eye_contour), (-1, 3))
        iris = np.reshape(np.squeeze(iris), (-1, 3))
        # normalize  # Q: what to do with z?
        eye_contour[:,0] /= input_shape[1]
        eye_contour[:,1] /= input_shape[2]
        iris[:,0] /= input_shape[1]
        iris[:,1] /= input_shape[2]

        return eye_contour.view(Vectors), iris.view(Vectors)

    def get_input_shape(self):
        input_shape = self._input_details[0]['shape']
        return [input_shape[1], input_shape[2]]  # 64 x 64 model input