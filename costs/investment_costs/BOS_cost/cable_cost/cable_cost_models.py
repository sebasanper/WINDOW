from numpy import sqrt
from costs.investment_costs.BOS_cost.cable_cost.Cables_cost_topology import cable_design
from farm_description import number_turbines_per_cable, central_platform, read_cablelist
from turbine_description import rated_current


def cable_optimiser(layout):
    return cable_design(layout)


def radial_cable(layout):

    cables_info = read_cablelist()
    Cable_List = []
    for number in number_turbines_per_cable:
        for cable in cables_info:
            if rated_current * number <= cable[1]:
                Cable_List.append([number, cable[2] + 365.0])
                break

    total_distance = 0.0
    for i in range(len(layout)):
        distance_one = sqrt((central_platform[0][0] - layout[i][1]) ** 2.0 + (central_platform[0][1] - layout[i][2]) ** 2.0)
        total_distance += distance_one
    cable_length = total_distance
    total_cost = cable_length * Cable_List[0][1]

    routes = []
    for turbine in layout:
        routes.append([[0, turbine[0] + 1]])
    routes_dict = {1: routes}

    return total_cost, routes_dict, cable_length


def random_cable(layout):
    import random
    cables_info = read_cablelist()
    Cable_List = []

    for number in number_turbines_per_cable:

        for cable in cables_info:

            if rated_current * number <= cable[1]:
                Cable_List.append([number, cable[2] + 365.0])
                break

    layout = [[item[0] + 1, item[1], item[2]] for item in layout]
    layout.insert(0, [0, central_platform[0][0], central_platform[0][1]])

    quantity = range(1, len(layout))

    routes = []
    for route in range(len(layout) / number_turbines_per_cable[0]):
        routes.append([])
        first_turbine = random.choice(quantity)
        routes[-1].append([0, first_turbine])
        quantity.pop(quantity.index(first_turbine))

        for turbine in range(min(number_turbines_per_cable[0] - 1, len(quantity))):

            random_number = random.choice(quantity)
            routes[-1].append([routes[-1][-1][1], random_number])
            quantity.pop(quantity.index(random_number))

    routes_dict = {1: routes}

    # print routes_dict
    total_distance = 0.0
    for i in range(len(routes)):
        summation = 0.0
        for j in range(len(routes[i])):

            distance_one = sqrt((layout[routes[i][j][0]][1] - layout[routes[i][j][1]][1]) ** 2.0 + (layout[routes[i][j][0]][2] - layout[routes[i][j][1]][2]) ** 2.0)
            # print distance_one, layout[routes[i][j][0]], layout[routes[i][j][1]]
            summation += distance_one
        total_distance += summation
    cable_length = total_distance
    total_cost = cable_length * Cable_List[0][1]

    return total_cost, routes_dict, cable_length


if __name__ == '__main__':
    l = radial_cable([[0, 500.0, 0.0], [1, 1000.0, 0.0], [2, 1500.0, 0.0], [3, 2000.0, 0.0], [4, 2500.0, 0.0], [5, 3000.0, 0.0], [6, 3500.0, 0.0], [7, 4000.0, 0.0]])
    m = cable_optimiser([[0, 500.0, 0.0], [1, 1000.0, 0.0], [2, 1500.0, 0.0], [3, 2000.0, 0.0], [4, 2500.0, 0.0], [5, 3000.0, 0.0], [6, 3500.0, 0.0], [7, 4000.0, 0.0]])
    n = random_cable([[0, 500.0, 0.0], [1, 1000.0, 0.0], [2, 1500.0, 0.0], [3, 2000.0, 0.0], [4, 2500.0, 0.0], [5, 3000.0, 0.0], [6, 3500.0, 0.0], [7, 4000.0, 0.0]])
    print l
    print m
    print n
