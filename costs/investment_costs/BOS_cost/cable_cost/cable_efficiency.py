def infield_efficiency(topology, wt_list, powers):

    from copy import deepcopy
    from farm_description import number_turbines_per_cable, read_cablelist
    from turbine_description import rated_power, rated_current

    cables_info = read_cablelist()
    Cable_area = []
    for number in number_turbines_per_cable:
        for cable in cables_info:
            if rated_current * number <= cable[1]:
                Cable_area.append([number, cable[0] / 1000000.0])
                break
    # print Cable_area

    def current_turbine(tree, coord):
        line2 = deepcopy(tree)

        def find_next(number, branch, outl):
            next_turbine = number
            for item in branch:
                if number == item[0]:
                    outl.append(item[1])
                    branch.remove(item)
                    next_turbine = item[1]
                elif number == item[1]:
                    outl.append(item[0])
                    branch.remove(item)
                    next_turbine = item[0]
            return next_turbine, branch, outl

        def find_ends(branch2):
            branch = deepcopy(branch2)
            all_elements = [item[i] for i in range(2) for item in branch]
            values = list(set(all_elements))
            values.remove(0)
            out_list = []
            for value in values:
                if all_elements.count(value) == 1:
                    out_list.append([value])
                    for i in range(100):
                        value, branch, out_list[-1] = find_next(value, branch, out_list[-1])
            return out_list

        tree_branches = find_ends(line2)

        def sort_branches(routes):
            def length(a):
                return len(a)
            routes.sort(key=length)
            if routes[-1][-1] != 0:
                for item in routes:
                    if item[-1] == 0:
                        routes.append(routes.pop(routes.index(item)))
            return routes

        sort_branches(tree_branches)

        all_elements = [item[i] for item in tree_branches for i in range(len(item))]

        def remove_dup(seq):
            seen = set()
            seen_add = seen.add
            return [x for x in seq if not (x in seen or seen_add(x))]

        def distance(t1, t2):
            return ((t1[1] - t2[1]) ** 2.0 + (t1[2] - t2[2]) ** 2.0) ** 0.5

        a = list(reversed(remove_dup(reversed(all_elements))))
        # print a
        counter = {n: [1, 0.0] for n in a}

        for n in a:
            for m in a:
                if [n, m] in line2 or [m, n] in line2:
                    if [n, m] in line2:
                        line2.remove([n, m])
                        counter[m][0] += counter[n][0]
                        counter[n][1] = distance(coord[n - 1], coord[m - 1])
                    if [m, n] in line2:
                        line2.remove([m, n])
                        counter[m][0] += counter[n][0]
                        counter[n][1] = distance(coord[n - 1], coord[m - 1])
                        # TODO solve distances of individual cables per number of turbines connected.

        return counter

    all_lines = topology[1]

    max_counter = [[0.0, []] for _ in range(100)]

    for line in all_lines:
        amount = current_turbine(line, wt_list)
        for i in range(10):
            for key in amount:
                if amount[key][0] == i + 1 and key != 0:
                    max_counter[i][0] += amount[key][1]
                    max_counter[i][1].append(key)
    # Provides the length of cables that carry the current
    #  of that number of turbines, and their ID. Index one is for one turbine, etc.

    current_squared_cables = [0.00 for _ in range(len(max_counter))]
    for i in range(len(max_counter)):
        for turbine in max_counter[i][1]:
            current_squared_cables[i] += (i + 1) ** 2.0 * (rated_current * powers[turbine - 1] / rated_power) ** 2.0
            #  Assumed linear current with power.

    losses = []  # Expresed in W.
    for i in range(len(max_counter)):
        losses.append(max_counter[i][0] * 1.74e-8 / Cable_area[0][1] * current_squared_cables[i] * 3.0)  # Three times the loss of each cable (* 3.0)

    # print sum(powers)  # Expressed in W originally.
    # print sum(losses)
    efficiency = 1.0 - sum(losses) / (sum(powers) * 1000.0)
    # print efficiency
    return efficiency

    # TODO: make function, input is cable topology, powers, output is losses (efficiency).

if __name__ == '__main__':
    turbines = [[0, 423974.0, 6151447.0], [1, 424033.0, 6150889.0], [2, 424092.0, 6150332.0], [3, 424151.0, 6149774.0], [4, 424210.0, 6149216.0], [5, 424268.0, 6148658.0], [6, 424327.0, 6148101.0], [7, 424386.0, 6147543.0], [8, 424534.0, 6151447.0], [9, 424593.0, 6150889.0], [10, 424652.0, 6150332.0], [11, 424711.0, 6149774.0], [12, 424770.0, 6149216.0], [13, 424829.0, 6148658.0], [14, 424888.0, 6148101.0], [15, 424947.0, 6147543.0], [16, 425094.0, 6151447.0], [17, 425153.0, 6150889.0], [18, 425212.0, 6150332.0], [19, 425271.0, 6149774.0], [20, 425330.0, 6149216.0], [21, 425389.0, 6148658.0], [22, 425448.0, 6148101.0], [23, 425507.0, 6147543.0], [24, 425654.0, 6151447.0], [25, 425713.0, 6150889.0], [26, 425772.0, 6150332.0], [27, 425831.0, 6149774.0], [28, 425890.0, 6149216.0], [29, 425950.0, 6148659.0], [30, 426009.0, 6148101.0], [31, 426068.0, 6147543.0], [32, 426214.0, 6151447.0], [33, 426273.0, 6150889.0], [34, 426332.0, 6150332.0], [35, 426392.0, 6149774.0], [36, 426451.0, 6149216.0], [37, 426510.0, 6148659.0], [38, 426569.0, 6148101.0], [39, 426628.0, 6147543.0], [40, 426774.0, 6151447.0], [41, 426833.0, 6150889.0], [42, 426892.0, 6150332.0], [43, 426952.0, 6149774.0], [44, 427011.0, 6149216.0], [45, 427070.0, 6148659.0], [46, 427129.0, 6148101.0], [47, 427189.0, 6147543.0], [48, 427334.0, 6151447.0], [49, 427393.0, 6150889.0], [50, 427453.0, 6150332.0], [51, 427512.0, 6149774.0], [52, 427571.0, 6149216.0], [53, 427631.0, 6148659.0], [54, 427690.0, 6148101.0], [55, 427749.0, 6147543.0], [56, 427894.0, 6151447.0], [57, 427953.0, 6150889.0], [58, 428013.0, 6150332.0], [59, 428072.0, 6149774.0], [60, 428132.0, 6149216.0], [61, 428191.0, 6148659.0], [62, 428250.0, 6148101.0], [63, 428310.0, 6147543.0], [64, 428454.0, 6151447.0], [65, 428513.0, 6150889.0], [66, 428573.0, 6150332.0], [67, 428632.0, 6149774.0], [68, 428692.0, 6149216.0], [69, 428751.0, 6148659.0], [70, 428811.0, 6148101.0], [71, 428870.0, 6147543.0], [72, 429014.0, 6151447.0], [73, 429074.0, 6150889.0], [74, 429133.0, 6150332.0], [75, 429193.0, 6149774.0], [76, 429252.0, 6149216.0], [77, 429312.0, 6148659.0], [78, 429371.0, 6148101.0], [79, 429431.0, 6147543.0]]
    topology_infield = {1: [[[0, 1], [1, 9], [9, 17], [17, 25], [25, 33]], [[0, 2], [2, 10], [10, 18], [18, 26], [26, 34]], [[0, 3], [3, 11], [11, 19], [19, 27], [27, 35]], [[0, 4], [4, 12], [12, 20], [20, 28], [28, 36]], [[0, 6], [6, 5], [5, 13], [13, 21], [21, 29]], [[0, 8], [8, 7]], [[0, 14], [14, 22], [22, 30], [30, 38], [38, 37]], [[0, 16], [16, 15], [15, 23], [23, 31]], [[0, 24], [24, 32]], [[0, 40], [40, 39]], [[0, 41], [41, 49], [49, 57], [57, 65], [65, 73]], [[0, 43], [43, 42], [42, 50], [50, 58], [58, 66]], [[0, 48], [48, 47], [47, 46], [46, 45], [45, 44]], [[0, 51], [51, 59], [59, 67], [67, 75], [75, 74]], [[0, 53], [53, 52], [52, 60], [60, 68], [68, 76]], [[0, 56], [56, 55], [55, 54]], [[0, 62], [62, 61], [61, 69], [69, 77], [77, 78]], [[0, 64], [64, 63]], [[0, 72], [72, 80], [80, 79], [79, 71], [71, 70]]]}
    power_farm = [2093565.835072073, 2093565.835072073, 2093565.835072073, 2093565.835072073, 2093565.835072073, 2093565.835072073, 2093565.835072073, 2093565.835072073, 970912.1639761042, 970912.1639761042, 970912.1639761042, 970912.1639761042, 970912.1639761042, 972028.8759749128, 972028.8759749128, 972028.8759749128, 856368.4900918187, 856368.4900918187, 856368.4900918187, 856368.4900918187, 856368.4900918187, 856562.6294422023, 856562.6294422023, 856562.6294422023, 817521.9688741626, 817521.9688741626, 817521.9688741626, 817521.9688741626, 817521.9688741626, 818649.4742934267, 818649.4742934267, 818649.4742934267, 800291.9176205526, 800291.9176205526, 800291.9176205526, 801349.2450845584, 801349.2450845584, 800561.9506871989, 800561.9506871989, 800561.9506871989, 790706.259114797, 790706.259114797, 790706.259114797, 790980.8610865711, 790980.8610865711, 790805.7814723507, 790805.7814723507, 791938.7514550166, 785247.4717865943, 785247.4717865943, 786373.5500075835, 785341.046856496, 785341.046856496, 786415.4026981284, 786415.4026981284, 785565.9733507703, 781909.309076278, 781909.309076278, 782186.9572632989, 781948.6236118248, 783070.2168610861, 782207.1326652362, 782207.1326652362, 783146.786443516, 779751.8367781838, 779751.8367781838, 779848.6898312533, 779770.8224566365, 780048.8760519167, 779859.4400662353, 780977.9745233878, 780081.3342479035, 778295.0209224396, 779411.3148292388, 778336.5917060911, 779421.4533680348, 778402.6835940181, 779459.097465536, 778620.9743479398, 779534.9774013254]

    # print infield_efficiency(topology_infield, turbines, power_farm), " %"
