from numpy import sqrt


def dist_line(a, b, c, x, y):
    return abs(a * x + b * y + c) / sqrt(a ** 2.0 + b ** 2.0)


def dist_point(x0, y0, x, y):
    return sqrt((x0 - x) ** 2.0 + (y0 - y) ** 2.0)

