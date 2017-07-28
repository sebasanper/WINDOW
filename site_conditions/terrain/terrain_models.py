from numpy import exp
from math import sqrt


def distance(x0, y0, x, y):
    return sqrt((x0 - x) ** 2.0 + (y0 - y) ** 2.0)


class Flat:
    def __init__(self, minx, maxx, miny, maxy):
        pass

    def depth(self, x, y):
        return 13.5


class Plane:
    def __init__(self, minx, maxx, miny, maxy):
        point1 = [maxx, maxy, 15]
        point2 = [minx, miny, 12.0]
        point3 = [minx, miny + 1.0, 12.0]
        self.point1 = [float(point1[i]) for i in range(3)]
        self.point2 = [float(point2[i]) for i in range(3)]
        self.point3 = [float(point3[i]) for i in range(3)]

    def depth(self, x, y):
        x1 = self.point1[0]
        x2 = self.point2[0]
        x3 = self.point3[0]
        y1 = self.point1[1]
        y2 = self.point2[1]
        y3 = self.point3[1]
        z1 = self.point1[2]
        z2 = self.point2[2]
        z3 = self.point3[2]

        return ((y - y1) * ((x2 - x1) * (z3 - z1) - (x3 - x1) * (z2 - z1)) - (x - x1) * ((y2 - y1) * (z3 - z1) - (z2 - z1) * (y3 - y1))) / ((x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)) + z1


class Gaussian:
    def __init__(self, minx, maxx, miny, maxy):
        self.centre = [minx + (maxx - minx) / 2.0, miny + (maxy - miny) / 2.0]
        self.sigma_x = distance(self.centre[0], self.centre[1], minx, miny) * 3.0 / 2.0  # Sigma is (max - desired value) times the distance from centre of rectangle to the sides, divided by two. Example: Rectangle is 4000x900. Centre at 2000x450. So 450 to one side, 450 * 3 = 1350 / 2 = 675.0. 3 is 15.0 m - 12.0 m (max - min water depth).
        self.sigma_y = self.sigma_x
        self.height = 15.0

    def depth(self, x, y):
        # print self.centre, self.sigma_x, self.sigma_y
        return self.height * exp(- ((x - self.centre[0]) ** 2.0 / 2.0 / self.sigma_x ** 2.0 + (y - self.centre[1]) ** 2.0 / 2.0 / self.sigma_y ** 2.0))


class Rough:

    def __init__(self, minx, maxx, miny, maxy):
        from random import random
        self.coordinates_x = [float(number) for number in range(int(minx), int(maxx), 504)]
        self.coordinates_y = [float(number) for number in range(int(miny), int(maxy), 504)]
        self.depths = [12.0 + random() * 3.0 for _ in range(len(self.coordinates_x) * len(self.coordinates_y))]
        # k = 0
        # for i in self.coordinates_x:
        #     for j in self.coordinates_y:
        #         print i, j, self.depths[k]
        #         k += 1

    def depth(self, x, y):
        from scipy.interpolate import interp2d
        degree = 'linear'  # 'cubic' 'quintic'
        function = interp2d(self.coordinates_x, self.coordinates_y, self.depths, kind=degree)
        return function(x, y)[0]


def depth(layout, model_type):
    terrain = model_type
    return [terrain.depth(layout[i][1], layout[i][2]) for i in range(len(layout))]


if __name__ == '__main__':
    minx = 260.0
    maxx = 4260.0
    miny = 9251.0
    maxy = 13251.0
    place1 = [[0, 2100.000000, 11251.000000]]
    place2 = [[0, 260.000000, 9251.000000]]
    place3 = [[0, 4260.000000, 13251.000000]]
    print depth(place1, Flat(minx, maxx, miny, maxy))
    print depth(place1, Gaussian(minx, maxx, miny, maxy))
    print depth(place2, Gaussian(minx, maxx, miny, maxy))
    print depth(place3, Gaussian(minx, maxx, miny, maxy))
    print depth(place1, Plane(minx, maxx, miny, maxy))
    print depth(place1, Rough(minx, maxx, miny, maxy))
