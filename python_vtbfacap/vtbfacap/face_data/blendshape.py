from pydantic.dataclasses import dataclass

from .stabilizer import Stabilizer


class Blendshape:
    pass


@dataclass
class Live2dShape:
    yaw: float = 0.5
    pitch: float = 0.5
    roll: float = 0.5

    _stablilizers = {}

    def update(self, face_and_iris_landmarks):
        self.yaw = self.stablize("yaw", face_and_iris_landmarks.yaw()) + 0.5
        self.pitch = self.stablize("pitch", face_and_iris_landmarks.pitch()) + 0.5
        self.roll = self.stablize("roll", face_and_iris_landmarks.roll()) + 0.5

    def stablize(self, name, value):
        stabilizer_name = f"{name}_stabilizer"
        if stabilizer_name not in self._stablilizers:
            self._stablilizers[stabilizer_name] = Stabilizer()
        return self._stablilizers[stabilizer_name].correct(value)

    def bytes(self):
        msg = " ".join([f"{getattr(self, name):.4f}" for name in self.__annotations__])
        return msg.encode("ascii")
