# -----------------------------------------Input Parameters------------------------------------------------------------------
from math import hypot
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from copy import deepcopy
from heapq import heappush, heappop, heapify
import matplotlib.ticker as ticker
from time import time


def cable_design(WT_List):
    central_platform_locations = [[497362.28738843824, 5730299.074285714], [503845.86170414777, 5727342.685714286]]
    NT = len(WT_List)
    # List of cable types: [Capacity,Cost] in increasing order (maximum 3 cable types)
    Cable_List = [[6, 256 + 365], [10, 406 + 365]]
    # Cable_List=[[5,110],[8,180]]
    # Cable_List=[[10,406+365]]
    Crossing_penalty = 0
    Area = []
    # Transmission = [[central_platform_locations[0], [463000, 5918000]],
    #                 [central_platform_locations[1], [463000, 5918000]]]
    Transmission = []

    'Remove and return the lowest priority task. Raise KeyError if empty.'
    REMOVED = '<removed-task>'  # placeholder for a removed task

    fontsize = 20
    fontsize2 = 5
    Euro = "eur"
    MEuro = "M%s" % Euro

    # ---------------------------------------Main--------------------------------------------------------------------------------
    def set_cable_topology(NT, WT_List, central_platform_locations, Cable_List):
        start = time()
        Wind_turbines = []
        for WT in WT_List:
            Wind_turbines.append([WT[0] + 1, WT[1], WT[2]])
        # initialize the parameters
        Wind_turbinesi, Costi, Cost0i, Costij, Savingsi, Savingsi_finder, Savingsi2, Savingsi2_finder, distancefromsubstationi, substationi, Routingi, Routing_redi, Routing_greeni, Routesi, Capacityi, Cable_Costi, Crossings_finder = dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict(), dict()
        i = 1
        for substation in central_platform_locations:
            Wind_turbinesi[i], Costi[i], distancefromsubstationi[i] = initial_values(NT, Wind_turbines, substation)
            substationi[i] = substation
            i += 1
        # splits the Wind_turbines list in the closest substation
        def second(x):
            return x[2]
        for j in xrange(NT):
            empty = []
            for key, value in distancefromsubstationi.iteritems():
                empty.append(value[j])
            index = empty.index(min(empty, key=second)) + 1
            Wind_turbinesi[index].append([value[j][1], Wind_turbines[j][1], Wind_turbines[j][2]])
        # Wind_turbinesi[1]=[x for x in Wind_turbines if x[0]<=118]
        #        Wind_turbinesi[2]=[x for x in Wind_turbines if x[0]>118]
        for j in xrange(len(Cable_List)):
            Capacityi[j + 1] = Cable_List[j][0]
            Cable_Costi[j + 1] = Cable_List[j][1]
        # initialize routes and Saving matrix
        for key, value in Wind_turbinesi.iteritems():
            Routesi[key], Routingi[key], Routing_redi[key], Routing_greeni[key] = initial_routes(value)
            Cost0i[key], Costij[key] = costi(value, substationi[key])
            Savingsi[key], Savingsi_finder[key], Crossings_finder[key] = savingsi(Cost0i[key], Costij[key], value,
                                                                                  Cable_Costi[1], substationi[key],
                                                                                  Area,
                                                                                  Crossing_penalty)
        # fig = plt.figure()
        # for area in Area:
        #     plt.plot([area[0][0], area[1][0]], [area[0][1], area[1][1]], color='k', ls='--', linewidth='2')
        # for trans in Transmission:
        #     plt.plot([trans[0][0], trans[1][0]], [trans[0][1], trans[1][1]], color='yellow', linewidth='4')
        cable_length = 0
        blue_length = 0.0
        red_length = 0.0
        total_cost = 0
        crossings = 0
        for key, value in Wind_turbinesi.iteritems():
            Routesi[key], Routingi[key], Routing_redi[key], Routing_greeni[key] = Hybrid(Savingsi[key], Savingsi_finder[key], Wind_turbinesi[key], Routesi[key], Routingi[key], substationi[key], Capacityi, Routing_redi[key], Routing_greeni[key], Costi[key], Cable_Costi)
            Savingsi2[key], Savingsi2_finder[key], Crossings_finder[key] = savingsi(Cost0i[key], Costij[key], value, Cable_Costi[1], substationi[key], Area, Crossing_penalty)
            Routesi[key], Routingi[key], Routing_redi[key], Routing_greeni[key] = Esau_Williams_Cable_Choice(Savingsi2[key], Savingsi2_finder[key], Crossings_finder[key], Wind_turbinesi[key], Routesi[key], Routingi[key], substationi[key], Capacityi, Routing_redi[key], Routing_greeni[key], Costi[key], Cable_Costi)
            Routesi[key], Routingi[key] = RouteOpt_Hybrid(Routingi[key], Routing_redi[key], Routing_greeni[key], substationi[key], Costi[key], Capacityi, Routesi[key], Wind_turbinesi[key])
            blue, red, cost = plotting(substationi[key], Wind_turbinesi[key], Routingi[key], Routing_redi[key], Routing_greeni[key], Capacityi, Cable_Costi)
            cable_length += blue + red
            blue_length += blue
            red_length += red
            total_cost += cost
            for route in Routingi[key]:
                if edge_crossings_area([route[0], route[1]], Wind_turbinesi[key], substationi[key], Area)[0] is True:
                    crossings += edge_crossings_area([route[0], route[1]], Wind_turbinesi[key], substationi[key], Area)[1]
        # print Routesi[1]
        # print Routingi[1]
        # print 'Cable length = {0} km'.format(round(cable_length / 1000, 3))
        # print 'Cable cost = {0:,} {1}'.format(round(total_cost / 1000000, 3), MEuro)
        # if Area is not []:
        #     print 'Crossings = {0}'.format(crossings)
        # print 'Elapsed time = {0:.3f} s'.format(time() - start)
        ######Legend######
        # if len(Cable_Costi) == 1:
        #     label1 = mpatches.Patch(color='blue',
        #                             label='Capacity: {0}'.format(Capacityi[1], round(cable_length / 1000, 3),
        #                                                          int(total_cost), name))
        #     legend = plt.legend([label1], ["Capacity: {0}".format(Capacityi[1])], loc='upper right', numpoints=1,
        #                         fontsize=fontsize2, fancybox=True, shadow=True, ncol=2,
        #                         title='Cable Cost: {0:,} {1}'.format(round(total_cost / 1000000, 3), MEuro))
        # elif len(Cable_Costi) == 2:
        #     label1 = mpatches.Patch(color='blue',
        #                             label='Capacity: {0}'.format(Capacityi[1], round(cable_length / 1000, 3),
        #                                                          int(total_cost)))
        #     label2 = mpatches.Patch(color='red',
        #                             label='Capacity: {1}'.format(Capacityi[2], round(cable_length / 1000, 3),
        #                                                          int(total_cost)))
        #     legend = plt.legend([label1, (label2)],
        #                         ["Capacity: {0}".format(Capacityi[1]), "Capacity: {0}".format(Capacityi[2])],
        #                         loc='upper right', numpoints=1, fontsize=fontsize2, fancybox=True, shadow=True, ncol=2,
        #                         title='Cable Cost: {0:,} {1}'.format(round(total_cost / 1000000, 3), MEuro))
        # elif len(Cable_Costi) == 3:
        #     label1 = mpatches.Patch(color='blue',
        #                             label='Capacity: {0}'.format(Capacityi[1], round(cable_length / 1000, 3),
        #                                                          int(total_cost)))
        #     label2 = mpatches.Patch(color='red',
        #                             label='Capacity: {1}'.format(Capacityi[2], round(cable_length / 1000, 3),
        #                                                          int(total_cost)))
        #     label3 = mpatches.Patch(color='green',
        #                             label='Capacity: {2}'.format(Capacityi[3], round(cable_length / 1000, 3),
        #                                                          int(total_cost)))
        #     legend = plt.legend([label1, label2, label3],
        #                         ["Capacity: {0}".format(Capacityi[1]), "Capacity: {0}".format(Capacityi[2]),
        #                          "Capacity: {0}".format(Capacityi[3])], loc='upper right', numpoints=1,
        #                         fontsize=fontsize2,
        #                         fancybox=True, shadow=True, ncol=3,
        #                         title='Cable Cost: {0:,} {1}'.format(round(total_cost / 1000000, 3), MEuro))
        # plt.setp(legend.get_title(), fontsize=fontsize2)
        # plt.tight_layout()
        # plt.subplots_adjust(left=0.06, right=0.94, bottom=0.08)
        # plt.gca().set_aspect('equal', adjustable='box')
        # # plt.title(' {0} OWF - Hybrid '.format(name), fontsize=fontsize)
        # plt.grid()
        # scale = 1000
        # ticks1 = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / scale))
        # ax.xaxis.set_major_formatter(ticks1)
        # ticks2 = ticker.FuncFormatter(lambda y, pos: '{0:g}'.format(y / scale))
        # ax.yaxis.set_major_formatter(ticks2)
        # plt.xticks(fontsize=fontsize2)
        # plt.yticks(fontsize=fontsize2)
        # # plt.show()
        # plt.savefig("topology.eps", format="eps", dpi=1000)

        I = 60.6060  # Current on cable of the v80 turbine
        rho = 0.0000000174  # Resistivity of copper at 20 degrees C
        A1 = 0.00015  # cross section cable current 375 A
        A2 = 0.0005  # cross section cable current 655 A. Katsouris Thesis

        losses = (I ** 2.0 * rho) * (6.0 ** 2.0 * blue_length / A1 + 10.0 ** 2.0 * red_length / A2)

        total_power = 233.0 * 2e6

        eff = 1.0 -losses / total_power

        return total_cost, cable_length, eff * 100.0

    def mainroutine(arc, lines, Routes, Routing):
        if [arc[0], 0] in Routing:
            index1 = Routing.index([arc[0], 0])
        else:
            for line in lines:
                if arc[0] in line:
                    index1 = Routing.index([line[0], 0])
        Routing.pop(index1)
        Routing.append([arc[0], arc[1]])
        # turbines to be reversed
        for line in lines:
            if arc[0] in line:
                indexline = lines.index(line)
                indexarc = line.index(arc[0])
        indeces = []
        for i in xrange(0, indexarc):
            turbine = lines[indexline][i]
            for route in Routing:
                if route[1] == turbine and route != [arc[0], arc[1]]:
                    indexroute = Routing.index(route)
                    indeces.append(indexroute)
        for index in indeces:
            Routing[index].reverse()
        Routes = []
        for route in Routing:
            if route[1] == 0:
                Routes.append([[route[1], route[0]]])
        helpRouting = [i for i in Routing if i[1] != 0]
        helpRouting.reverse()
        for path in Routes:
            for pair in path:
                for route in helpRouting:
                    if pair[1] == route[1]:
                        index2 = path.index(pair)
                        index3 = Routes.index(path)
                        Routes[index3].insert(index2 + 1, [route[1], route[0]])
        indeces = []
        for zeygos in helpRouting:
            for path in Routes:
                if [zeygos[1], zeygos[0]] in path:
                    indexzeygos = helpRouting.index(zeygos)
                    indeces.append(indexzeygos)
        for index in indeces:
            helpRouting[index] = []
        temp = [x for x in helpRouting if x != []]
        temp2 = []
        for pair1 in temp:
            counter1 = 1
            counter2 = 1
            for pair2 in temp:
                if pair1[0] in pair2 and pair2 != pair1:
                    counter1 += 1
            if [pair1[0], counter1] not in temp2:
                temp2.append([pair1[0], counter1])
            for pair2 in temp:
                if pair1[1] in pair2 and pair2 != pair1:
                    counter2 += 1
            if [pair1[1], counter2] not in temp2:
                temp2.append([pair1[1], counter2])
        temp3 = []
        for pair1 in temp2:
            for pair2 in temp:
                if pair1[1] == 1 and pair1[0] == pair2[0]:
                    temp3.append(pair2)
                    temp.remove(pair2)

        for pair1 in temp3:
            for pair2 in temp:
                if pair1[1] == pair2[0]:
                    indexpair1 = temp3.index(pair1)
                    temp3.insert(indexpair1 + 1, pair2)
                    temp.remove(pair2)
        temp3 = [x for x in temp if x not in temp3] + temp3
        indeces = []
        if temp3 != []:
            for pair in temp3:
                for route in Routes:
                    for path in route:
                        if pair[0] == path[1]:
                            indexpath = route.index(path)
                            indexroute = Routes.index(route)
                            Routes[indexroute].insert(indexpath + 1, pair)
                            indextemp = temp3.index(pair)
                            indeces.append(indextemp)
            for index in indeces:
                temp3[index] = []
            while temp3 != []:
                indeces = []
                temp3 = [x for x in temp3 if x != []]
                temp3.reverse()
                for pair in temp3:
                    for route in Routes:
                        for path in route:
                            if pair[1] == path[1]:
                                indexpath = route.index(path)
                                indexroute = Routes.index(route)
                                Routes[indexroute].insert(indexpath + 1, [pair[1], pair[0]])
                                indextemp = temp3.index(pair)
                                indeces.append(indextemp)
                for index in indeces:
                    temp3[index] = []
                if temp3 != []:
                    temp3 = [x for x in temp3 if x != []]
                    indeces = []
                    temp3.reverse()
                    for pair in temp3:
                        for route in Routes:
                            for path in route:
                                if pair[0] == path[1]:
                                    indexpath = route.index(path)
                                    indexroute = Routes.index(route)
                                    Routes[indexroute].insert(indexpath + 1, pair)
                                    indextemp = temp3.index(pair)
                                    indeces.append(indextemp)
                    for index in indeces:
                        temp3[index] = []
                    temp3 = [x for x in temp3 if x != []]
        return Routing, Routes

    def Hybrid(Savingsi, Savingsi_finder, Wind_turbinesi, Routes, Routing, central_platform_location, Capacityi,
               Routing_red, Routing_green, Costi, Cable_Costi):
        Paths = []
        for WT in Wind_turbinesi:
            Paths.append([0, WT[0]])
        while True:
            if Savingsi:
                Savingsi, Savingsi_finder, saving = pop_task(Savingsi, Savingsi_finder)
            else:
                break
            if saving is None or saving[0] > 0:
                break
            arc = [saving[1], saving[2]]
            if check_same_path(arc, Paths) is False and any(
                    [True for e in [[arc[0], 0]] if e in Routing]) is True and one_neighbor(arc[1], Paths) is False:
                condition4 = dict()
                for key, value in Capacityi.iteritems():
                    condition4[key] = check_capacity(arc, Paths, Capacityi[key])
                if condition4[1] == False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) == False and edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[0] == False:
                    Routing = []
                    for index1, path in enumerate(Paths):
                        if arc[0] == path[1]:
                            Paths[index1].remove(0)
                            break
                    for index2, path in enumerate(Paths):
                        if arc[1] == path[-1]:
                            break
                    Paths[index2] = Paths[index2] + Paths[index1]
                    Paths[index1] = []
                    Paths = [path for path in Paths if path != []]
                    for i in Paths:
                        for j in xrange(len(i) - 1):
                            Routing.append([i[j + 1], i[j]])
        Routes = []
        for index, path in enumerate(Paths):
            route = []
            for j in xrange(len(path) - 1):
                route.append([path[j], path[j + 1]])
            Routes.append(route)
        return Routes, Routing, Routing_red, Routing_green

    def Esau_Williams_Cable_Choice(Savingsi, Savingsi_finder, Crossingsi_finder, Wind_turbinesi, Routes, Routing,
                                   central_platform_location, Capacityi, Routing_red, Routing_green, Costi,
                                   Cable_Costi):
        total_update_red = []
        total_update_green = []
        while True:
            if Savingsi:
                Savingsi, Savingsi_finder, saving = pop_task(Savingsi, Savingsi_finder)
            else:
                break
            if saving is None or saving[0] > 0:
                break
            arc = [saving[1], saving[2]]
            lines = turbinesinroute(Routes)
            if check_same_path(arc, lines) is False:
                condcap = dict()
                for key, value in Capacityi.iteritems():
                    condcap[key] = check_capacityEW(arc, lines, Capacityi[key])
                if condcap[1] is False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] == False and edge_crossings(arc, Wind_turbinesi, central_platform_location,
                                                       Routing) == False:
                        Routing, Routes = mainroutine(arc, lines, Routes, Routing)
                        lines = turbinesinroute(Routes)
                        for indexl, line in enumerate(lines):
                            if arc[0] in line:
                                break
                        for turbine in lines[indexl]:
                            for n in Wind_turbinesi:
                                value = -(Costi[lines[indexl][0]][0] - Costi[turbine][n[0]]) * Cable_Costi[1]
                                arc1 = [lines[indexl][0], 0]
                                arc2 = [turbine, n[0]]
                                if turbine != n[0]:
                                    value += Crossing_penalty * (Crossingsi_finder[(arc2[0], arc2[1])] - Crossingsi_finder[(arc1[0], arc1[1])])
                                Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (turbine, n[0]), value)
                        heapify(Savingsi)
                if len(condcap) > 1 and condcap[1] == True and condcap[2] == False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] is False and edge_crossings(arc, Wind_turbinesi, central_platform_location,
                                                       Routing) is False:
                        Routes_temp = deepcopy(Routes)
                        Routing_temp = deepcopy(Routing)
                        total_update_red_temp = []
                        Routing_temp, Routes_temp = mainroutine(arc, lines, Routes_temp, Routing_temp)
                        lines = turbinesinroute(Routes_temp)
                        for indexl, line in enumerate(lines):
                            if arc[0] in line:
                                break
                        update = []
                        for route in Routes_temp:
                            for i in xrange(0, len(route)):
                                if arc[1] in route[i]:
                                    index = Routes_temp.index(route)
                        elements = len(Routes_temp[index])
                        if elements == 1:
                            index1 = len(Routes_temp[index][0]) - 1 - Capacityi[1]
                            for j in xrange(0, index1):
                                update.append([Routes_temp[index][0][j + 1], Routes_temp[index][0][j]])
                        connected_turbines = []
                        if elements > 1:
                            for i in xrange(0, elements):
                                for j in xrange(len(Routes_temp[index][elements - 1 - i]) - 1, 0, -1):
                                    connected_turbines.append([Routes_temp[index][elements - 1 - i][j - 1],
                                                               Routes_temp[index][elements - 1 - i][j], 1])
                        for pair1 in connected_turbines:
                            for pair2 in connected_turbines:
                                if pair1[0] == pair2[1]:
                                    index = connected_turbines.index(pair2)
                                    connected_turbines[index][2] = connected_turbines[index][2] + pair1[2]
                        for pair in connected_turbines:
                            if pair[2] > Capacityi[1]:
                                update.append([pair[1], pair[0]])
                        total_update_red_temp = renew_update(total_update_red, total_update_red_temp,
                                                             Routes_temp) + update
                        Routing_red_temp = []
                        for route in total_update_red_temp:
                            for z in xrange(0, len(route) - 1):
                                Routing_red_temp.append([route[z], route[z + 1]])
                        new = -(cable_cost(central_platform_location, Wind_turbinesi, Routing, Routing_red, Routing_green, Cable_Costi) - cable_cost(central_platform_location, Wind_turbinesi,  Routing_temp, Routing_red_temp, Routing_green,  Cable_Costi))
                        arc1 = [lines[indexl][0], 0]
                        new += Crossing_penalty * (Crossingsi_finder[(arc[0], arc[1])] - Crossingsi_finder[(arc1[0], arc1[1])])
                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (arc[0], arc[1]), new)
                        Savingsi, Savingsi_finder, max_saving = pop_task(Savingsi, Savingsi_finder)
                        if max_saving[0] == new:
                            Routes = Routes_temp
                            Routing = Routing_temp
                            Routing_red = Routing_red_temp
                            total_update_red = total_update_red_temp
                            lines = turbinesinroute(Routes)
                            for line in lines:
                                if arc[0] in line:
                                    indexl = lines.index(line)
                            for turbine in lines[indexl]:
                                for n in Wind_turbinesi:
                                    value = -(Costi[lines[indexl][0]][0] - Costi[turbine][n[0]]) * Cable_Costi[1]
                                    arc1 = [lines[indexl][0], 0]
                                    arc2 = [turbine, n[0]]
                                    if turbine != n[0]:
                                        value += Crossing_penalty * (Crossingsi_finder[(arc2[0], arc2[1])] - Crossingsi_finder[(arc1[0], arc1[1])])
                                    Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (turbine, n[0]),
                                                                         value)
                            heapify(Savingsi)
                        else:
                            Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder,
                                                                 (max_saving[1], max_saving[2]),
                                                                 max_saving[0])

                if len(condcap) > 2 and condcap[1] is True and condcap[2] is True and condcap[3] is False:
                    if edge_crossings_area(arc, Wind_turbinesi, central_platform_location, Transmission)[
                        0] is False and edge_crossings(arc, Wind_turbinesi, central_platform_location, Routing) is False:
                        Routes_temp = deepcopy(Routes)
                        Routing_temp = deepcopy(Routing)
                        total_update_red_temp = deepcopy(total_update_red)
                        total_update_green_temp = deepcopy(total_update_green)
                        Routing_temp, Routes_temp = mainroutine(arc, lines, Routes_temp, Routing_temp)
                        lines = turbinesinroute(Routes_temp)
                        for indexl, line in enumerate(lines):
                            if arc[0] in line:
                                break
                        update_red = []
                        update_green = []
                        for route in Routes_temp:
                            for i in xrange(0, len(route)):
                                if arc[1] in route[i]:
                                    index = Routes_temp.index(route)
                        elements = len(Routes_temp[index])
                        if elements == 1:
                            index1 = len(Routes_temp[index][0]) - 1 - Capacityi[1]
                            index2 = len(Routes_temp[index][0]) - 1 - Capacityi[2]
                            for j in xrange(index2, index1):
                                update_red.append([Routes_temp[index][0][j + 1], Routes_temp[index][0][j]])
                            for j in xrange(0, index2):
                                update_green.append([Routes_temp[index][0][j + 1], Routes_temp[index][0][j]])
                        connected_turbines = []
                        if elements > 1:
                            for i in xrange(0, elements):
                                for j in xrange(len(Routes_temp[index][elements - 1 - i]) - 1, 0, -1):
                                    connected_turbines.append([Routes_temp[index][elements - 1 - i][j - 1],
                                                               Routes_temp[index][elements - 1 - i][j], 1])
                        for pair1 in connected_turbines:
                            for pair2 in connected_turbines:
                                if pair1[0] == pair2[1]:
                                    index = connected_turbines.index(pair2)
                                    connected_turbines[index][2] = connected_turbines[index][2] + pair1[2]
                        for pair in connected_turbines:
                            if pair[2] > Capacityi[2]:
                                update_green.append([pair[1], pair[0]])
                            elif pair[2] > Capacityi[1] and pair[2] <= Capacityi[2]:
                                update_red.append([pair[1], pair[0]])

                        for pair in update_red:
                            if pair not in total_update_red_temp:
                                total_update_red_temp.append(pair)
                        total_update_red_temp = [x for x in total_update_red_temp if x in Routing_temp]

                        for pair in update_green:
                            if pair not in total_update_green_temp:
                                total_update_green_temp.append(pair)
                        total_update_green_temp = [x for x in total_update_green_temp if x in Routing_temp]

                        total_update_red_temp = [x for x in total_update_red_temp if x not in total_update_green_temp]

                        Routing_red_temp = []
                        for route in total_update_red_temp:
                            for z in xrange(0, len(route) - 1):
                                Routing_red_temp.append([route[z], route[z + 1]])
                        Routing_green_temp = []
                        for route in total_update_green_temp:
                            for z in xrange(0, len(route) - 1):
                                Routing_green_temp.append([route[z], route[z + 1]])
                        arc1 = [lines[indexl][0], 0]
                        new = new + Crossing_penalty * (
                            Crossingsi_finder[arc[0], arc[1]] - Crossingsi_finder[arc1[0], arc1[1]])
                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (arc[0], arc[1]), new)
                        Savingsi, Savingsi_finder, max_saving = pop_task(Savingsi, Savingsi_finder)
                        if max_saving[0] == new:
                            Routes = Routes_temp
                            Routing = Routing_temp
                            Routing_red = Routing_red_temp
                            Routing_green = Routing_green_temp
                            total_update_red = total_update_red_temp
                            total_update_green = total_update_green_temp
                            lines = turbinesinroute(Routes)
                            for line in lines:
                                if arc[0] in line:
                                    indexl = lines.index(line)
                            for turbine in lines[indexl]:
                                for n in Wind_turbinesi:
                                    if turbine != n[0]:
                                        value = -(Costi[lines[indexl][0]][0] - Costi[turbine][n[0]]) * Cable_Costi[1]
                                        arc1 = [lines[indexl][0], 0]
                                        arc2 = [turbine, n[0]]
                                        value = value + Crossing_penalty * (
                                            Crossingsi_finder[arc2[0], arc2[1]] - Crossingsi_finder[arc1[0], arc1[1]])
                                        Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder, (turbine, n[0]),
                                                                             value)
                            heapify(Savingsi)
                        else:
                            Savingsi, Savingsi_finder = add_task(Savingsi, Savingsi_finder,
                                                                 (max_saving[1], max_saving[2]),
                                                                 max_saving[0])
        return Routes, Routing, Routing_red, Routing_green

    def RouteOpt_Hybrid(Routing, Routing_red, Routing_green, central_platform_location, Costi, Capacityi, Routes,
                        Wind_turbinesi):
        Paths = []
        temp = []
        for route in Routes:
            cond = False
            for i in range(len(route) - 1, -1, -1):
                for pair in route:
                    if route[i][0] == pair[0] and route[i] != pair and cond == False:
                        cond = True
                        for pair5 in route:
                            if pair[0] == pair5[0]:
                                path = []
                                path.append(pair5[0])
                                path.append(pair5[1])
                                for pair6 in route:
                                    if pair6[0] == path[-1]:
                                        path.append(pair6[1])
                                Paths.append(path)
                        temp.append(route)
            if cond == False and len(route) <= Capacityi[1]:
                path = []
                path.append(route[0][0])
                for pair in route:
                    path.append(pair[1])
                Paths.append(path)
            elif cond == False and len(route) > Capacityi[1]:
                index = len(route) - Capacityi[1]
                path = []
                path.append(route[index][0])
                for i in range(index, len(route)):
                    path.append(route[i][1])
                Paths.append(path)
        before = []
        after = []
        def first(x):
            return x[0]
        for path in Paths:
            list = []
            index = Paths.index(path)
            path.reverse()
            cond = True
            i = 0
            while cond == True:
                for l in range(1, len(path)):
                    list.append([Costi[path[l - 1]][path[l]] - Costi[path[l]][path[0]], path[0], path[l]])
                s = max(list, key=first)
                if s[0] > 0 and edge_crossings([s[1], s[2]], Wind_turbinesi, central_platform_location,
                                               Routing) == False and \
                                edge_crossings_area([s[1], s[2]], Wind_turbinesi, central_platform_location,
                                                    Transmission)[
                                    0] == False:
                    for k in list:
                        if k == s:
                            lamd = list.index(k)
                            xmm = lamd + 1
                            path1 = path[:xmm]
                            path2 = path[xmm:]
                            path1.reverse()
                            if i == 0:
                                before.append(Paths[index])
                            i = 1
                            path = path1 + path2
                            Paths[index] = path
                            list = []
                            cond = True
                else:
                    list = []
                    cond = False
                    if i == 1:
                        after.append(Paths[index])

        for path in before:
            for i in range(0, len(path) - 1):
                if [path[i], path[i + 1]] in Routing:
                    Routing.remove([path[i], path[i + 1]])
                elif [path[i + 1], path[i]] in Routing:
                    Routing.remove([path[i + 1], path[i]])
        for path in after:
            for i in range(0, len(path) - 1):
                Routing.append([path[i], path[i + 1]])
        return Routes, Routing

    def renew_update(total_update, total_update_temp, Paths_temp):
        indeces = []
        for indexerase, route in enumerate(total_update):
            for turbine in route:
                if turbine != 0:
                    for pair in total_update_temp:
                        if (pair[0] != 0 and pair[1] == 0) or (pair[0] == 0 and pair[1] != 0):
                            same1 = [turbine, pair[0]]
                        if pair[0] != 0 and pair[1] != 0:
                            same1 = [turbine, pair[0]]
                            same2 = [turbine, pair[1]]
                            if check_same_path(same1, Paths_temp) == True or check_same_path(same2, Paths_temp) == True:
                                if indexerase not in indeces:
                                    indeces.append(indexerase)
        if indeces != []:
            for i in indeces:
                total_update[i] = []
        for pair in total_update[:]:
            if pair == []:
                total_update.remove(pair)
        return total_update

    def initial_values(NT, Wind_turbines, central_platform_location):
        Costi = [[0 for i in xrange(NT + 1)] for j in xrange(NT + 1)]
        set_cost_matrix(Costi, Wind_turbines, central_platform_location)
        distancefromsubstationi = []
        for i in xrange(len(Costi[0]) - 1):
            distancefromsubstationi.append([0, i + 1, Costi[0][i + 1]])
        Wind_turbinesi = []
        return Wind_turbinesi, Costi, distancefromsubstationi

    def initial_routes(Wind_turbinesi):
        Routing_greeni = []
        Routing_redi = []
        Routingi = []
        Routesi = []
        for WT in Wind_turbinesi:
            Routingi.append([WT[0], 0])
            Routesi.append([[0, WT[0]]])
        return Routesi, Routingi, Routing_redi, Routing_greeni

    def check_same_path(arc, Paths):
        same_path = False
        for path in Paths:
            if arc[0] in path and arc[1] in path:
                same_path = True
                break
        return same_path

    # Subroutine 5, check if turbine u has only one neighbor in Routing
    def one_neighbor(turbine, Paths):
        more_than_one = False
        for path in Paths:
            if turbine in path and turbine != path[-1]:
                more_than_one = True
                break
        return more_than_one

    def costi(Wind_turbinesi, central_platform_location):
        Cost0i = []
        Costij = []
        for i in Wind_turbinesi:
            Cost0i.append([0, i[0], hypot(central_platform_location[0] - i[1], central_platform_location[1] - i[2])])
            for j in Wind_turbinesi:
                if i != j:
                    Costij.append([i[0], j[0], hypot(i[1] - j[1], i[2] - j[2])])
        return Cost0i, Costij

    def savingsi(Cost0i, Costij, Wind_turbinesi, Cable_Cost1, central_platform_location, Area, Crossing_penalty):
        Savingsi = []
        Savingsi_finder = {}
        Crossingsi_finder = {}
        counter = 0
        for i in zip(*Wind_turbinesi)[0]:
            k = Cost0i[counter]
            step = (len(Wind_turbinesi) - 1) * counter
            for j in xrange(step, step + len(Wind_turbinesi) - 1):
                saving = -(k[2] - Costij[j][2]) * Cable_Cost1
                arc1 = [i, 0]
                arc2 = [i, Costij[j][1]]
                crossings_arc1 = edge_crossings_area(arc1, Wind_turbinesi, central_platform_location, Area)[1]
                crossings_arc2 = edge_crossings_area(arc2, Wind_turbinesi, central_platform_location, Area)[1]
                Crossingsi_finder[(arc1[0], arc1[1])] = crossings_arc1
                Crossingsi_finder[(arc2[0], arc2[1])] = crossings_arc2
                saving = saving + Crossing_penalty * (crossings_arc2 - crossings_arc1)
                if saving < 0:
                    add_task(Savingsi, Savingsi_finder, (i, Costij[j][1]), saving)
            counter += 1
        return Savingsi, Savingsi_finder, Crossingsi_finder

    def add_task(Savings, entry_finder, task, priority):
        'Add a new task or update the priority of an existing task'
        if task in entry_finder:
            entry_finder = remove_task(entry_finder, task)
        entry = [priority, task[0], task[1]]
        entry_finder[(task[0], task[1])] = entry
        heappush(Savings, entry)
        return Savings, entry_finder

    def remove_task(entry_finder, task):
        entry = entry_finder.pop(task)
        entry[0] = REMOVED
        return entry_finder

    def pop_task(Savings, entry_finder):
        while Savings:
            saving = heappop(Savings)
            if saving[0] is not REMOVED:
                del entry_finder[(saving[1], saving[2])]
                return Savings, entry_finder, saving

    def set_cost_matrix(Cost, Wind_turbines, central_platform_location):
        Cost[0][0] = float('inf')
        for i in Wind_turbines:
            Cost[0][i[0]] = hypot(central_platform_location[0] - i[1], central_platform_location[1] - i[2])
            Cost[i[0]][0] = hypot(central_platform_location[0] - i[1], central_platform_location[1] - i[2])
            for j in Wind_turbines:
                if i == j:
                    Cost[i[0]][j[0]] = float('inf')
                else:
                    Cost[i[0]][j[0]] = hypot(i[1] - j[1], i[2] - j[2])

    def turbinesinroute(Routes):
        lines = [[] for i in xrange(len(Routes))]
        for route in Routes:
            index = Routes.index(route)
            for pair in route:
                lines[index].append(pair[1])
        return lines

    def check_capacityEW(arc, Paths, Capacity):
        cap_exceeded = False
        turbines_in_branch = 0
        for path in Paths:
            if arc[0] in path or arc[1] in path:
                turbines_in_branch = turbines_in_branch + (len(path))
                if turbines_in_branch > Capacity:
                    cap_exceeded = True
                    break
        return cap_exceeded

    def check_capacity(arc, Paths, Capacity):
        cap_exceeded = False
        turbines_in_branch = 0
        for path in Paths:
            if arc[0] in path or arc[1] in path:
                turbines_in_branch = turbines_in_branch + (len(path) - 1)
                if turbines_in_branch > Capacity:
                    cap_exceeded = True
                    break
        return cap_exceeded

    def edge_crossings(arc, Wind_turbines, central_platform_location, Routing):
        x1, y1 = give_coordinates(arc[0], Wind_turbines, central_platform_location)
        x2, y2 = give_coordinates(arc[1], Wind_turbines, central_platform_location)
        intersection = False
        # Left - 0
        # Right - 1
        # Colinear - 2
        for route in Routing:
            if arc[0] not in route:
                x3, y3 = give_coordinates(route[0], Wind_turbines, central_platform_location)
                x4, y4 = give_coordinates(route[1], Wind_turbines, central_platform_location)
                counter = 0
                Area = [0, 0, 0, 0]
                Position = [0, 0, 0, 0]
                Area[0] = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
                Area[1] = (x2 - x1) * (y4 - y1) - (x4 - x1) * (y2 - y1)
                Area[2] = (x4 - x3) * (y1 - y3) - (x1 - x3) * (y4 - y3)
                Area[3] = (x4 - x3) * (y2 - y3) - (x2 - x3) * (y4 - y3)
                for i in xrange(4):
                    if Area[i] > 0:
                        Position[i] = 0
                    elif Area[i] < 0:
                        Position[i] = 1
                    else:
                        Position[i] = 2
                        counter += 1
                if Position[0] != Position[1] and Position[2] != Position[3] and counter <= 1:
                    intersection = True
                    break
        return intersection

    def edge_crossings_area(arc, Wind_turbines, central_platform_location, Area_cross):
        x1, y1 = give_coordinates(arc[0], Wind_turbines, central_platform_location)
        x2, y2 = give_coordinates(arc[1], Wind_turbines, central_platform_location)
        intersection = False
        crossings = 0
        for area in Area_cross:
            counter = 0
            x3, y3 = area[0][0], area[0][1]
            x4, y4 = area[1][0], area[1][1]
            Area = [0, 0, 0, 0]
            Position = [0, 0, 0, 0]
            Area[0] = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
            Area[1] = (x2 - x1) * (y4 - y1) - (x4 - x1) * (y2 - y1)
            Area[2] = (x4 - x3) * (y1 - y3) - (x1 - x3) * (y4 - y3)
            Area[3] = (x4 - x3) * (y2 - y3) - (x2 - x3) * (y4 - y3)
            for i in xrange(4):
                if Area[i] > 0:
                    Position[i] = 0
                elif Area[i] < 0:
                    Position[i] = 1
                else:
                    Position[i] = 2
                    counter += 1
            if Position[0] != Position[1] and Position[2] != Position[3] and counter <= 1:
                intersection = True
                crossings += 1
        return intersection, crossings

    # Plotting+Cable_length
    def plotting(central_platform_location1, Wind_turbines1, Routing, Routing_red, Routing_green, Capacityi,
                 Cable_Costi):
        central_platform_location1_1 = [[0, central_platform_location1[0], central_platform_location1[1]]]
        Full_List = central_platform_location1_1 + Wind_turbines1
        Routing_blue = [i for i in Routing if i not in Routing_red]
        Routing_blue = [i for i in Routing_blue if i not in Routing_green]
        cable_length1blue = 0
        index, x, y = zip(*Full_List)
        # ax = fig.add_subplot(111)
        # ax.set_xlabel('x [km]', fontsize=fontsize2)
        # ax.set_ylabel('y [km]', fontsize=fontsize2)
        arcs1 = []
        arcs2 = []
        for i in Routing_blue:
            for j in Full_List:
                if j[0] == i[0]:
                    arcs1.append([j[1], j[2]])
                if j[0] == i[1]:
                    arcs2.append([j[1], j[2]])
        for i in xrange(len(arcs1)):
            arcs1.insert(2 * i + 1, arcs2[i])
        for j in xrange(len(arcs1) - len(Routing_blue)):
            # plt.plot([arcs1[2 * j][0], arcs1[2 * j + 1][0]], [arcs1[2 * j][1], arcs1[2 * j + 1][1]], color='b')
            cable_length1blue = cable_length1blue + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                                          arcs1[2 * j][1] - arcs1[2 * j + 1][1])
        cable_cost = Cable_Costi[1] * cable_length1blue
        cable_length = cable_length1blue

        if len(Cable_Costi) == 2:
            cable_length1red = 0
            arcs1 = []
            arcs2 = []
            for i in Routing_red:
                for j in Full_List:
                    if j[0] == i[0]:
                        arcs1.append([j[1], j[2]])
                    if j[0] == i[1]:
                        arcs2.append([j[1], j[2]])
            for i in xrange(len(arcs1)):
                arcs1.insert(2 * i + 1, arcs2[i])
            for j in xrange(len(arcs1) - len(Routing_red)):
                # plt.plot([arcs1[2 * j][0], arcs1[2 * j + 1][0]], [arcs1[2 * j][1], arcs1[2 * j + 1][1]], color='r')
                cable_length1red = cable_length1red + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                                            arcs1[2 * j][1] - arcs1[2 * j + 1][1])
            cable_cost = Cable_Costi[1] * cable_length1blue + Cable_Costi[2] * cable_length1red
            cable_length = cable_length1blue + cable_length1red

        if len(Cable_Costi) == 3:

            cable_length1red = 0
            arcs1 = []
            arcs2 = []
            for i in Routing_red:
                for j in Full_List:
                    if j[0] == i[0]:
                        arcs1.append([j[1], j[2]])
                    if j[0] == i[1]:
                        arcs2.append([j[1], j[2]])
            for i in xrange(len(arcs1)):
                arcs1.insert(2 * i + 1, arcs2[i])
            for j in xrange(len(arcs1) - len(Routing_red)):
                # plt.plot([arcs1[2 * j][0], arcs1[2 * j + 1][0]], [arcs1[2 * j][1], arcs1[2 * j + 1][1]], color='r')
                cable_length1red = cable_length1red + hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                                            arcs1[2 * j][1] - arcs1[2 * j + 1][1])

            cable_length1green = 0
            arcs1 = []
            arcs2 = []
            for i in Routing_green:
                for j in Full_List:
                    if j[0] == i[0]:
                        arcs1.append([j[1], j[2]])
                    if j[0] == i[1]:
                        arcs2.append([j[1], j[2]])
            for i in xrange(len(arcs1)):
                arcs1.insert(2 * i + 1, arcs2[i])
            for j in xrange(len(arcs1) - len(Routing_green)):
                # plt.plot([arcs1[2 * j][0], arcs1[2 * j + 1][0]], [arcs1[2 * j][1], arcs1[2 * j + 1][1]], color='g')
                cable_length1green += hypot(arcs1[2 * j][0] - arcs1[2 * j + 1][0],
                                            arcs1[2 * j][1] - arcs1[2 * j + 1][1])
            cable_length = cable_length1blue + cable_length1red + cable_length1green
            cable_cost = Cable_Costi[1] * cable_length1blue + Cable_Costi[2] * cable_length1red + Cable_Costi[3] * cable_length1green
        # plt.plot([p[1] for p in central_platform_location1_1], [p[2] for p in central_platform_location1_1], marker='o', ms=10, color='0.35')
        # plt.plot([p[1] for p in Wind_turbines1], [p[2] for p in Wind_turbines1], 'o', ms=6, color='0.3')

        return cable_length1blue, cable_length1red, cable_cost

    def cable_cost(central_platform_location, Wind_turbinesi, Routing, Routing_red, Routing_green, Cable_Costi):
        Routing_blue = [i for i in Routing if i not in Routing_red]
        Routing_blue = [i for i in Routing_blue if i not in Routing_green]
        cable_length1blue = 0
        for route in Routing_blue:
            x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
            x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
            cable_length1blue = cable_length1blue + hypot(x2 - x1, y2 - y1)
        cable_cost = Cable_Costi[1] * (cable_length1blue)

        if len(Cable_Costi) == 2:
            cable_length1red = 0
            for route in Routing_red:
                x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
                x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
                cable_length1red = cable_length1red + hypot(x2 - x1, y2 - y1)
            cable_cost = Cable_Costi[1] * (cable_length1blue) + Cable_Costi[2] * (cable_length1red)

        if len(Cable_Costi) == 3:
            cable_length1red = 0
            for route in Routing_red:
                x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
                x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
                cable_length1red = cable_length1red + hypot(x2 - x1, y2 - y1)
            cable_length1green = 0
            for route in Routing_green:
                x1, y1 = give_coordinates(route[0], Wind_turbinesi, central_platform_location)
                x2, y2 = give_coordinates(route[1], Wind_turbinesi, central_platform_location)
                cable_length1green = cable_length1green + hypot(x2 - x1, y2 - y1)
            cable_cost = Cable_Costi[1] * (cable_length1blue) + Cable_Costi[2] * (cable_length1red) + Cable_Costi[3] * (
                cable_length1green)
        return cable_cost

    # Submethods return x and y coordinates of a turbine if it's ID is known. The OHVS must also be included
    def give_coordinates(turbineID, Wind_turbines, central_platform_location):
        if turbineID == 0:
            x = central_platform_location[0]
            y = central_platform_location[1]
        else:
            turbine = WT_List[turbineID - 1]
            x = turbine[1]
            y = turbine[2]
        return x, y

    return set_cable_topology(NT, WT_List, central_platform_locations, Cable_List)


# ------------------------------------Run------------------------------------------------------------------

if __name__ == '__main__':
    # ---------------------------------------Input--------------------------------------------------------------------------------
    # name = 'Borssele'
    WT_List = [[0, 485101.04983316606, 5732217.3257142855], [1, 485503.6486449828, 5731759.337142857],
               [2, 485866.01741583704, 5731311.565714286], [3, 486268.61622765375, 5730792.548571428],
               [4, 486671.24216694245, 5732675.28], [5, 487089.95469712175, 5732217.3257142855],
               [6, 487444.23948132276, 5731708.457142857], [7, 487846.86542061146, 5731250.502857143],
               [8, 487846.86542061146, 5733591.222857143], [9, 488249.4642324282, 5733061.988571429],
               [10, 488660.1199034262, 5732624.4], [11, 489014.43181509915, 5732166.411428572],
               [12, 489425.0874860972, 5731657.577142857], [13, 489827.7134253859, 5731199.622857143],
               [14, 489425.0874860972, 5733998.297142857], [15, 489827.7134253859, 5733530.16],
               [16, 490238.3690963839, 5733021.291428572], [17, 490592.65388058487, 5732563.337142857],
               [18, 491003.3366790549, 5732095.2], [19, 491405.9354908716, 5731596.514285714],
               [20, 491808.5614301603, 5733479.245714285], [21, 492170.9030735426, 5732960.228571429],
               [22, 492581.5587445406, 5732502.274285714], [23, 492984.1846838293, 5732034.137142858],
               [24, 494152.1579903969, 5735245.577142857], [25, 494553.2647912541, 5734783.68],
               [26, 494963.2965303963, 5734321.782857143], [27, 495319.8328947725, 5733803.554285714],
               [28, 495720.93969562976, 5735684.938285714], [29, 496130.971434772, 5735166.72],
               [30, 496541.0031739142, 5734716.102857143], [31, 496897.5395382904, 5734265.451428572],
               [32, 497307.57127743267, 5736090.504], [33, 497708.6780782899, 5735628.610285714],
               [34, 489415.4029785964, 5729387.485714286], [35, 489820.4161354203, 5728866.377142857],
               [36, 490184.08702493017, 5728396.285714285], [37, 490589.07305428205, 5727947.108571429],
               [38, 490994.086211106, 5727435.222857143], [39, 491407.34611941513, 5726975.588571428],
               [40, 491762.7431299677, 5726526.411428572], [41, 490994.086211106, 5729775.188571429],
               [42, 491407.34611941513, 5729315.554285714], [43, 491771.0170089249, 5728803.702857143],
               [44, 492167.72915931966, 5728354.491428572], [45, 492581.0161951008, 5727894.857142857],
               [46, 492977.7283454955, 5727435.222857143], [47, 492977.7283454955, 5729712.514285714],
               [48, 493349.6731139625, 5729263.337142857], [49, 493746.4123918292, 5728803.702857143],
               [50, 494556.41157800506, 5730172.148571429], [51, 492974.7985785205, 5725094.708571428],
               [52, 493341.1279602854, 5724641.794285715], [53, 493755.25594769826, 5724128.468571428],
               [54, 494153.43298158044, 5723665.474285714], [55, 494511.78688658006, 5723212.56],
               [56, 493747.2804709329, 5726463.565714286], [57, 494153.43298158044, 5726000.571428572],
               [58, 494511.78688658006, 5725487.28], [59, 494917.93939722754, 5725044.411428572],
               [60, 495332.06738464045, 5724571.337142857], [61, 494909.9910479342, 5727379.508571428],
               [62, 495324.0919078751, 5726856.102857143], [63, 495722.2689417573, 5726403.188571429],
               [64, 496080.6499742289, 5725950.274285714], [65, 495722.2689417573, 5728738.285714285],
               [66, 496128.4214524049, 5728224.96], [67, 496494.75083416974, 5727782.125714285],
               [68, 496892.95499552396, 5727319.131428571], [69, 496892.95499552396, 5729593.817142857],
               [70, 497299.0803786995, 5729140.9028571425], [71, 497705.232889347, 5728677.908571429],
               [72, 498071.56227111194, 5730509.76], [73, 498477.7147817595, 5730056.811428571],
               [74, 496082.4403873803, 5721297.565714286], [75, 496497.110924233, 5720823.737142857],
               [76, 496894.71828120336, 5720378.64], [77, 496889.0215120853, 5722668.754285715],
               [78, 497297.9952798199, 5722202.125714285], [79, 497667.2001736158, 5721749.828571429],
               [80, 498070.50429970433, 5721225.771428571], [81, 498473.7812983208, 5720780.6742857145],
               [82, 498837.31655047066, 5720314.045714286], [83, 499240.62067655916, 5719876.114285714],
               [84, 499643.8976751756, 5719344.857142857], [85, 500041.50503214606, 5718899.76],
               [86, 500410.737053414, 5718440.297142857], [87, 497655.86089032365, 5724025.577142857],
               [88, 498064.8075305862, 5723558.948571429], [89, 498468.1116566747, 5723106.651428571],
               [90, 498871.4157827632, 5722604.125714285], [91, 499240.62067655916, 5722144.662857143],
               [92, 499643.8976751756, 5721692.4], [93, 500041.50503214606, 5721225.771428571],
               [94, 500410.737053414, 5720723.245714285], [95, 500808.3444103844, 5720263.782857143],
               [96, 498466.9180479071, 5725386.377142857], [97, 498878.8487100887, 5724931.851428571],
               [98, 499238.47760627186, 5724469.062857143], [99, 499643.87054770364, 5724014.537142857],
               [100, 500042.72576838563, 5723502.137142858], [101, 500454.68355803925, 5723047.611428572],
               [102, 500820.8501749722, 5722593.085714285], [103, 501219.7053956542, 5722080.72],
               [104, 499226.080351572, 5726806.422857143], [105, 499635.02699183463, 5726298.514285714],
               [106, 500048.9922144155, 5725835.142857143], [107, 500452.8660174158, 5725380.685714286],
               [109, 501206.0874047148, 5724461.348571429], [108, 500819.49380137265, 5724849.84],
               [110, 500043.94650462526, 5728169.794285715], [111, 500452.8660174158, 5727661.885714286],
               [112, 500812.440658655, 5727198.514285714], [113, 501221.36017144565, 5726752.971428571],
               [114, 501623.25366899057, 5726236.148571429], [115, 501221.36017144565, 5729025.257142857],
               [116, 501630.3068117082, 5728570.8], [117, 502032.1731817812, 5728125.257142857],
               [118, 498462.27925019665, 5732385.12], [119, 499640.1540840409, 5733242.228571429],
               [120, 500044.678946369, 5732783.588571428], [121, 500449.20380869706, 5732324.948571429],
               [122, 501621.1377261753, 5730911.451428572], [123, 500445.7857472262, 5734610.777142857],
               [124, 500858.2589588476, 5734151.417142857], [125, 501217.48094295093, 5733680.777142857],
               [126, 501222.55378021323, 5735978.989714285], [127, 501621.1377261753, 5735520.342857143],
               [128, 502031.6035048694, 5735069.245714285], [129, 502783.82117570465, 5731772.468571428],
               [130, 502421.94069934625, 5736879.929142857], [131, 502785.88286357594, 5736427.9954285715],
               [132, 503194.55822911864, 5735911.505142857], [133, 503603.2064671893, 5735467.645714286],
               [134, 503181.78118981095, 5738251.858285714], [135, 503603.2064671893, 5737799.928],
               [136, 504005.47974934214, 5737339.926857143], [137, 505180.37056126737, 5735919.576],
               [138, 506757.5346553455, 5733974.6742857145], [139, 507115.1018636573, 5733522.72],
               [140, 507523.804356672, 5733062.742857143], [141, 507932.3440848547, 5732562.377142857],
               [142, 503961.66888207686, 5730339.6342857145], [143, 504370.69690475543, 5729889.12],
               [144, 504773.919648428, 5729416.457142857], [145, 504364.8644982774, 5732222.914285715],
               [146, 504779.752054906, 5731772.4], [147, 505177.1152646285, 5731248.034285714],
               [148, 505539.40265306673, 5730797.52], [149, 505948.4306757453, 5730347.005714286],
               [150, 506357.48582589586, 5729822.6742857145], [151, 506760.6814420964, 5729364.754285715],
               [152, 507117.1092965846, 5728914.274285714], [153, 507526.2458291512, 5728397.28],
               [154, 507923.39201909775, 5727946.765714286], [155, 505182.94767110655, 5733581.794285715],
               [156, 505591.9756937851, 5733131.314285714], [157, 505942.5982692673, 5732629.0971428575],
               [158, 506351.62629194587, 5732156.434285714], [159, 506754.8219081464, 5731705.92],
               [160, 507122.96883053466, 5731203.737142857], [161, 507526.2458291512, 5730745.817142857],
               [162, 507929.36006293574, 5730280.56], [163, 508332.4742967203, 5729763.565714286],
               [164, 508688.92927868053, 5729313.085714285], [165, 501973.27944008895, 5716503.462857143],
               [166, 502388.62816374144, 5716045.165714285], [167, 502790.79293600627, 5715595.165714285],
               [168, 503153.40585410845, 5715070.217142857], [169, 503562.1897295391, 5714620.2514285715],
               [170, 503964.354501804, 5714161.954285714], [171, 501979.8714157828, 5718844.937142857],
               [172, 502388.62816374144, 5718378.308571429], [173, 502790.79293600627, 5717870.022857143],
               [174, 503199.5768114369, 5717420.057142857], [175, 503555.59775384533, 5716953.428571428],
               [176, 503964.354501804, 5716445.108571429], [177, 504366.5192740688, 5715986.811428571],
               [178, 504729.159319643, 5715528.514285714], [179, 505137.91606760165, 5715020.228571429],
               [180, 502388.62816374144, 5720661.497142857], [181, 502797.3849117001, 5720203.165714285],
               [182, 503199.5768114369, 5719744.868571429], [183, 503555.59775384533, 5719236.582857143],
               [184, 503964.354501804, 5718778.285714285], [185, 504373.11124976265, 5718311.657142857],
               [186, 504781.8951251933, 5717811.702857143], [187, 505137.91606760165, 5717353.371428572],
               [188, 505540.08083986654, 5716886.742857143], [189, 505955.45669099095, 5716445.108571429],
               [190, 502790.7115535903, 5722545.531428572], [191, 503196.9454466538, 5722024.32],
               [192, 503553.97010552586, 5721573.12], [193, 503966.3619347313, 5721121.885714286],
               [194, 504372.6229552668, 5720600.6742857145], [195, 504772.69891218835, 5720141.657142857],
               [196, 505135.88150720234, 5719690.457142857], [197, 505542.11540026584, 5719239.257142857],
               [198, 505948.37642080133, 5718725.794285715], [199, 506351.62629194587, 5718259.028571429],
               [200, 506711.6349727369, 5717815.611428572], [201, 503196.9454466538, 5724358.182857143],
               [202, 503603.2064671893, 5723922.514285714], [203, 503960.20399858936, 5723393.52],
               [204, 504366.46501912485, 5722942.285714285], [205, 504772.69891218835, 5722483.302857143],
               [206, 505135.88150720234, 5722024.32], [207, 505542.11540026584, 5721510.857142857],
               [208, 505948.37642080133, 5721059.657142857], [209, 506354.61031386483, 5720600.6742857145],
               [210, 506717.7929088788, 5720087.2114285715], [211, 507117.8688658004, 5719628.228571429],
               [212, 503594.17301901634, 5726185.371428572], [213, 503964.354501804, 5725724.3657142855],
               [214, 504367.2245883406, 5725270.2514285715], [215, 504770.06754740526, 5724822.994285714],
               [216, 505134.8235357947, 5724313.851428571], [217, 505548.5717385997, 5723839.0971428575],
               [218, 505945.98920326616, 5723384.982857143], [219, 506354.28478420095, 5722882.697142857],
               [220, 506713.5881507202, 5722421.691428571], [221, 507116.43110978487, 5721967.577142857],
               [222, 507524.6181808317, 5721458.4], [223, 504775.5201692754, 5727100.457142857],
               [224, 505172.9376339419, 5726639.485714286], [225, 505537.6664948593, 5726185.371428572],
               [226, 505951.4146976643, 5725669.302857143], [227, 506354.28478420095, 5725215.188571429],
               [228, 506713.5881507202, 5724761.074285714], [229, 507116.43110978487, 5724245.04],
               [230, 507524.6181808317, 5723790.925714286], [231, 507927.7324146163, 5723336.811428571],
               [232, 507927.7324146163, 5725614.274285714], [233, 508286.9001437756, 5725167.051428571]]
    # central_platform_locations=[[497362.28738843824, 5730299.074285714], [503845.86170414777, 5727342.685714286]]
    # NT = len(WT_List)
    # # List of cable types: [Capacity,Cost] in increasing order (maximum 3 cable types)
    # Cable_List = [[6, 256 + 365], [10, 406 + 365]]
    # # Cable_List=[[5,110],[8,180]]
    # # Cable_List=[[10,406+365]]
    # Crossing_penalty = 0
    # Area = []
    # # Transmission = [[central_platform_locations[0], [463000, 5918000]],
    # #                 [central_platform_locations[1], [463000, 5918000]]]
    # Transmission = []

    # set_cable_topology(NT, WT_List, central_platform_locations, Cable_List)
    print cable_design(WT_List)
    # from math import sqrt
    # platform = [[497362.28738843824, 5730299.074285714], [503845.86170414777, 5727342.685714286]]
    # length1 = 0.0
    # length2 = 0.0
    # for i in range(len(WT_List)):
    #     d1 = sqrt((platform[0][0] - WT_List[i][1]) ** 2.0 + (platform[0][1] - WT_List[i][2]) ** 2.0)
    #     d2 = sqrt((platform[1][0] - WT_List[i][1]) ** 2.0 + (platform[1][1] - WT_List[i][2]) ** 2.0)
    #     if d1 >= d2:
    #         length1 += d1
    #     else:
    #         length2 += d2
    # print length1, length2, (length1 + length2) / 233.0