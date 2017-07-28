from Hybrid import set_cable_topology
from random import randint

name = 'Borssele'
WT_List = [[0, 0.0, 0.0], [1, 0.0, 1000.0], [2, 0.0, 2000.0], [3, 0.0, 3000.0], [4, 1000.0, 0.0], [5, 1000.0, 1000.0], [6, 1000.0, 2000.0], [7, 1000.0, 3000.0], [8, 2000.0, 0.0], [9, 2000.0, 1000.0], [10, 2000.0, 2000.0], [11, 2000.0, 3000.0], [12, 3000.0, 0.0], [13, 3000.0, 3000.0], [14, 3000.0, 2000.0], [15, 3000.0, 3000.0]]

Cable_List = [[2, 1.0]]
Crossing_penalty = 0
Area = []
Transmission = []

with open("platform.dat", "a") as outf:

    for n in range(5):
        central_platform_locations = [[randint(0, 3000), randint(0, 3000)], [randint(0, 3000), randint(0, 3000)]]

        a = set_cable_topology(WT_List, central_platform_locations, Cable_List, Area, Transmission, Crossing_penalty)

        outf.write("{0} {1} {2}\n".format(a, central_platform_locations[0][0], central_platform_locations[0][1]))

