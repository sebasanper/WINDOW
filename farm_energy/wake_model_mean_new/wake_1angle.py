from .order_layout import order
#
# class Wake1Angle:
#     def __init__(self, thrust_coefficient, wake_model, wake_merging, aero_power):
#         # print "Model parameter must be Jensen, Larsen, Ainslie1D or Ainslie2D without quotation marks.\n"
#         self.WakeModel = wake_model
#         self.CT = thrust_coefficient
#         self.overlap = wake_merging
#         self.power = aero_power
#
#     def wake_one_angle(self, original_layout, freestream_wind_speed, wind_angle, ambient_turbulence):
#         ordered_layout = order(original_layout, wind_angle)
#         ct = []
#         wind_speeds_array = [freestream_wind_speed]
#         deficit_matrix = [[] for _ in range(len(ordered_layout))]
#         total_deficit = [0.0]
#         for i in range(len(ordered_layout)):
#             # start = time()
#             if i == 0:
#                 pass
#             else:
#                 total_deficit.append(root_sum_square([deficit_matrix[j][i] for j in range(i)]))
#                 wind_speeds_array.append(freestream_wind_speed * (1.0 - total_deficit[i]))
#             ct.append(self.CT(wind_speeds_array[i]))
#             deficit_matrix[i] = [0.0 for _ in range(i + 1)]
#             deficit_matrix[i] += self.WakeModel(ordered_layout[i], ct[i], [item for item in ordered_layout[i + 1:]], wind_angle, freestream_wind_speed, ambient_turbulence)
#             # print time() - start, wind_angle, i
#         # print deficit_matrix
#         wind_speeds_array_original = [x for (y, x) in sorted(zip([item[1] for item in ordered_layout], wind_speeds_array), key=lambda pair: pair[0])]
#         powers = [self.power(turbine_wind) for turbine_wind in wind_speeds_array_original]
#         return powers


def energy_one_angle(original_layout, freestream_wind_speeds, probabilities_speed, wind_angle, ambient_turbulences, WakeModel, PowerModel, power_lookup_file, ThrustModel, thrust_lookup_file, MergingModel):
    ordered_layout = order(original_layout, wind_angle)
    energy = 0.0
    weighted_individuals = [0.0 for _ in range(len(original_layout))]

    def first(x):
        return x[0]
    for speed in range(len(freestream_wind_speeds)):
        # print freestream_wind_speeds[speed]
        ct = []
        wind_speeds_array = [freestream_wind_speeds[speed]]
        deficit_matrix = [[] for _ in range(len(ordered_layout))]
        total_deficit = [0.0]
        for i in range(len(ordered_layout)):
            if i == 0:
                pass
            else:
                total_deficit.append(MergingModel([deficit_matrix[j][i] for j in range(i)]))
                wind_speeds_array.append(freestream_wind_speeds[speed] * (1.0 - total_deficit[i]))
            ct.append(ThrustModel(wind_speeds_array[i], thrust_lookup_file))
            deficit_matrix[i] = [0.0 for _ in range(i + 1)]
            deficit_matrix[i] += WakeModel(ordered_layout[i], ct[i], ordered_layout[i + 1:], wind_angle, freestream_wind_speeds[speed], ambient_turbulences[speed])
        wind_speeds_array_original = [x for (y, x) in sorted(zip([item[0] for item in ordered_layout], wind_speeds_array), key=first)]
        individual_powers = [PowerModel(wind, power_lookup_file) for wind in wind_speeds_array_original]
        for turb in range(len(individual_powers)):
            weighted_individuals[turb] += individual_powers[turb] * probabilities_speed[speed] / 100.0
        farm_power = sum(individual_powers)
        energy += farm_power * probabilities_speed[speed] / 100.0 * 8760.0
        # print speed, farm_power, probabilities_speed[speed], energy
        # print freestream_wind_speeds[speed], wind_speeds_array_original, individual_powers
    return energy, weighted_individuals


if __name__ == '__main__':

    from aero_power_ct_models.thrust_coefficient import v80, ct_v80
    from downstream_effects import Ainslie2DEffects as Ainslie2D, JensenEffects as Jensen
    from aero_power_ct_models.aero_models import power_v80
    from wake_overlap import root_sum_square

    layout = [[0, 0.0, 0.0], [1, 0.0, 1000.0], [2, 0.0, 2000.0], [3, 0.0, 3000.0], [4, 0.0, 4000.0], [5, 1000.0, 0.0], [6, 1000.0, 1000.0], [7, 1000.0, 2000.0], [8, 1000.0, 3000.0], [9, 1000.0, 4000.0], [10, 2000.0, 0.0], [11, 2000.0, 1000.0], [12, 2000.0, 2000.0], [13, 2000.0, 3000.0], [14, 2000.0, 4000.0], [15, 3000.0, 0.0], [16, 3000.0, 1000.0], [17, 3000.0, 2000.0], [18, 3000.0, 3000.0], [19, 3000.0, 4000.0], [20, 4000.0, 0.0], [21, 4000.0, 1000.0], [22, 4000.0, 2000.0], [23, 4000.0, 3000.0], [24, 4000.0, 4000.0]]
    U_inf = [8.5, 16]
    I0 = [0.08, 0.08]
    prob = [50.0, 50.0]
    # for angle in range(360):
    # print energy_one_angle(layout, U_inf, prob, 0.0, I0, Jensen, power_v80, v80, root_sum_square)
