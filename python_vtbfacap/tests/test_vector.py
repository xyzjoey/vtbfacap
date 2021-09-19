from vtbfacap.math_utils import Vectors, Ray, Plane


def test_project():
    a = Vectors.init([2, 0, 6])
    b = Vectors.init([3, 4, -3])

    assert list(a.project(b)) == [-1.0588235294117647, -1.411764705882353, 1.0588235294117647]


def test_ray_plane_intersect():
    plane_point_right = Vectors.init([0.52405, 0.31801, -0.00565])
    plane_point_left = Vectors.init([0.60278, 0.30092, -0.02866])
    plane_point_up = Vectors.init([0.56632, 0.29245, -0.02881])
    plane_point_down = Vectors.init([0.56296, 0.32295, -0.02779])
    point_to_project = Vectors.init([0.57234, 0.30640, 0.72887])

    plane_right = plane_point_right - plane_point_left
    plane_up = plane_point_up - plane_point_down
    plane_normal = plane_up.cross(plane_right).normalize()

    ray = Ray(point_to_project, Vectors.init([0, 0, -1]))
    plane = Plane(plane_point_right, plane_normal)

    intersect, t = Vectors.ray_plane_intersect(ray, plane)
    assert t == 0.7486349014605332
    assert list(intersect) == [0.57234, 0.3064, -0.019764901460533224]
