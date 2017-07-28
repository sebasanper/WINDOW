from random import random
from math import sin, cos, radians, sqrt
from turbine_description import rotor_radius


def distance(t1_x, t1_y, t2_x, t2_y):
    return abs(sqrt((t1_x - t2_x) ** 2.0 + (t1_y - t2_y) ** 2.0))


class AreaGiven:
    def __init__(self, p1=None, p2=None, p3=None, p4=None):
        if p1 is None:
            p1 = [0.0, 0.0]
        if p2 is None:
            p2 = [4000.0, 0.0]
        if p3 is None:
            p3 = [0.0, 4000.0]
        if p4 is None:
            p4 = [4000.0, 4000.0]
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4


def random_rectangle(n_turbines, area):
    diam = rotor_radius * 2.0
    from random import randint

    def gen_layout(n_turbines):
        return [gen_turbine() for _ in range(n_turbines)]

    def gen_turbine():
        a = [float(randint(area.p1[0], area.p4[0])), float(randint(area.p1[1], area.p4[1]))]
        return a

    def repair_distance(layout):
        n = 0
        while n == 0:
            n = 1
            for i in range(n_turbines):
                for j in range(n_turbines):
                    if i != j and distance(layout[i][0], layout[i][1], layout[j][0], layout[j][1]) < diam:
                        # print 'counting'
                        layout[j] = gen_turbine()
                        n = 0
        return layout

    layout = gen_layout(n_turbines)
    layout = repair_distance(layout)

    with open("layout_creator/random_layout4.dat", "w") as regular_file:
        print "archivo"
        for item in layout:
            regular_file.write("{0}\t{1}\n".format(item[0], item[1]))
    return layout


area1 = AreaGiven()
print random_rectangle(20, area1)
