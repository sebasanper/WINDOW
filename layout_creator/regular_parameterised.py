from random import random
from math import sin, cos, radians


class AreaGiven:
    def __init__(self, p1=None, p2=None, p3=None, p4=None):
        if p1 is None:
            p1 = [0.0, 0.0]
        if p2 is None:
            p2 = [0.0, 100.0]
        if p3 is None:
            p3 = [100.0, 0.0]
        if p4 is None:
            p4 = [100.0, 100.0]
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        random1 = random()
        random2 = random()
        self.starting_p = [p1[0] + random1 * (p3[0] - p1[0]), p2[0] + random2 * (p4[0] - p2[0])]
        print self.starting_p


def square_layout(dx, dy, dh, n_rows, n_columns, area, angle):

    angle = radians(angle)
    x0 = area.p1[0]
    y0 = area.p1[1]
    layout = [[[0, 0] for _ in range(n_columns)] for _ in range(n_rows)]
    layout[0][0] = [x0, y0]

    for j in range(1, n_columns):
        if j % 2 == 0:
            layout[0][j] = [layout[0][j - 1][0] - dh, layout[0][j - 1][1] + dy]

        else:
            layout[0][j] = [layout[0][j - 1][0] + dh, layout[0][j - 1][1] + dy]

    for i in range(1, n_rows):
        layout[i][0] = [layout[i - 1][0][0] + dx, layout[i - 1][0][1]]

        for j in range(1, n_columns):
            if j % 2 == 0:
                layout[i][j] = [layout[i][j - 1][0] - dh, layout[i][j - 1][1] + dy]

            else:
                layout[i][j] = [layout[i][j - 1][0] + dh, layout[i][j - 1][1] + dy]

    for i in range(n_rows):

        for j in range(n_columns):

            layout[i][j] = [layout[i][j][0] * (cos(angle)) - layout[i][j][1] * sin(angle), layout[i][j][0] * (sin(angle)) + layout[i][j][1] * cos(angle)]

    with open("regular_3x5_rotated2.dat", "w") as regular_file:
        for i in range(n_rows):
            for j in range(n_columns):
                regular_file.write("{0}\t{1}\n".format(layout[i][j][0], layout[i][j][1]))
    return layout


if __name__ == '__main__':
    area1 = AreaGiven()
    print square_layout(882.0, 450.0, 441.0, 5, 3, area1, 60.0)
