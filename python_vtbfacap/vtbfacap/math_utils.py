import numpy as np


class Mathf:
    @staticmethod
    def map(value, old_min=0, old_max=1, new_min=0, new_max=1):
        old_range = old_max - old_min
        new_range = new_max - new_min
        return (value - old_min) * (new_range / old_range) + new_min


class Vectors(np.ndarray):  # (-1, 3) or (-1, 2) or (3,) or (2,)
    class Columns:
        def __getitem__(self, *args):
            return np.c_.__getitem__(*args).view(Vectors)

    class Rows:
        def __getitem__(self, *args):
            return np.r_.__getitem__(*args).view(Vectors)

    c_ = Columns()
    r_ = Rows()

    @classmethod
    def init(cls, *args, **kw):
        return np.array(*args, **kw).view(cls)

    # @classmethod
    # def zeros(cls, *args, **kw):
    #     return np.zeros(*args, **kw).view(cls)

    # @classmethod
    # def ones(cls, *args, **kw):
    #     return np.ones(*args, **kw).view(cls)

    @classmethod
    def empty(cls, *args, **kw):
        return np.empty(*args, **kw).view(cls)

    @classmethod
    def origin(cls):
        return np.zeros(3).view(cls)

    def append_columns(self, value):
        if self.is_1d():
            return Vectors.r_[self, [value]]
        else:
            return Vectors.c_[self, np.ones(self.shape[0]) * value]

    def is_1d(self):
        return self.ndim == 1

    def length(self):
        return np.sqrt((self**2).sum())
    
    def lengths(self):
        if self.is_1d():
            return np.array(self.length())
        else:
            return np.sqrt((self**2).sum(axis=1))

    def normalize(self):
        lengths = self.lengths()
        return self / lengths if lengths != 0 else self

    def center(self):
        if self.is_1d():
            return self
        else:
            return self.mean(axis=0)

    def vectors2(self):
        return self[:2] if self.is_1d() else self[:, :2]

    def vectors3(self, z=1):
        return self.append_columns(z)

    def angle(self, v):  # assume 1d  # radian
        return np.arccos(self.dot(v) / (self.length() * v.length()))

    def cross(self, v):
        return np.cross(self, v).view(Vectors)

    def transform(self, M, origin=None):
        if origin is None:
            return (M @ self.T).T
        else:
            return (M @ (self - origin).T).T + origin

    def project(self, *vectors):
        projected = Vectors.origin()
        for v in vectors:
            projected += self.dot(v) * v
        return projected


class Transform2:
    @staticmethod
    def rotation(theta):
        s = np.sin(theta)
        c = np.cos(theta)
        return Vectors.init([
            [c, -s, 0],
            [s, c, 0],
            [0, 0, 1],
        ])

    @staticmethod
    def flip():
        return Vectors.init([
            [-1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ])
