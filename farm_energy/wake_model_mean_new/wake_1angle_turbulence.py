from farm_energy.wake_model_mean_new.order_layout import order
from utilities.min_distance.distance_algorithm import dist_point
from turbine_description import rotor_radius
from memoize import Memoize


def turbulence_one_angle(original_layout, freestream_wind_speed, wind_angle, ambient_turbulence, WakeModel, ThrustModel, thrust_file, TurbulenceModel):
    ordered_layout = order(original_layout, wind_angle)
    ct = []
    wind_speeds_array = freestream_wind_speed
    deficit_matrix = [[] for _ in range(len(ordered_layout))]
    front = []
    for i in range(len(ordered_layout)):
        ct.append(ThrustModel(wind_speeds_array, thrust_file))
        deficit_matrix[i] = [0.0 for _ in range(i + 1)]
        deficit_matrix[i] += WakeModel(ordered_layout[i], ct[i], ordered_layout[i + 1:], wind_angle, freestream_wind_speed, ambient_turbulence)
    transposed = [list(x) for x in zip(*deficit_matrix)]
    for i in range(len(transposed)):
        lista = transposed[i]
        if len(set(lista)) <= 1:
            front.append(float("inf"))
            continue
        maximo = max(lista)
        indice = lista.index(maximo)
        indice_maximo = ordered_layout[indice][0]
        front.append(indice_maximo)
    # print front
    a = zip([item[0] for item in ordered_layout], front)
    # print a

    def first(x):
        return x[0]

    turbine_affects = sorted(a, key=first)

    wake_added_turbulence = []
    for item in turbine_affects:
        if float("inf") in item:
            wake_added_turbulence.append(ambient_turbulence)
        else:
            wake_added_turbulence.append(TurbulenceModel(ambient_turbulence, ThrustModel(freestream_wind_speed, thrust_file), freestream_wind_speed, dist_point(original_layout[item[0]][1], original_layout[item[0]][2], original_layout[item[1]][1], original_layout[item[1]][2]) / (2.0 * rotor_radius)))

    return wake_added_turbulence
# turbulence_one_angle = Memoize(turbulence_one_angle)


def max_turbulence_one_angle(original_layout, windspeeds, wind_angle, turbulences, WakeModel, ThrustModel, thrust_file, TurbulenceModel):
    maximo = [0.0 for _ in range(len(original_layout))]
    for i in range(len(windspeeds)):
        maxturb = turbulence_one_angle(original_layout, windspeeds[i], wind_angle, turbulences[i], WakeModel, ThrustModel, thrust_file, TurbulenceModel)
        for j in range(len(original_layout)):
            if maxturb[j] > maximo[j]:
                maximo[j] = maxturb[j]
    return maximo
# max_turbulence_one_angle = Memoize(max_turbulence_one_angle)

if __name__ == '__main__':

    from farm_energy.wake_model_mean_new.aero_power_ct_models.thrust_coefficient import v80
    from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power_coefficient, thrust_coefficient, power_v80
    from farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen
    from farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2

    def average(lista):
        return sum([item / len(lista) for item in lista])

    layout = [[0, 0.0, 0.0], [1, 0.0, 900.0], [2, 0.0, 1800.0], [3, 0.0, 2700.0], [4, 0.0, 3600.0], [5, 900.0, 0.0], [6, 900.0, 900.0], [7, 900.0, 1800.0], [8, 900.0, 2700.0], [9, 900.0, 3600.0], [10, 1800.0, 0.0], [11, 1800.0, 900.0], [12, 1800.0, 1800.0], [13, 1800.0, 2700.0], [14, 1800.0, 3600.0], [15, 2700.0, 0.0], [16, 2700.0, 900.0], [17, 2700.0, 1800.0], [18, 2700.0, 2700.0], [19, 2700.0, 3600.0], [20, 3600.0, 0.0], [21, 3600.0, 900.0], [22, 3600.0, 1800.0], [23, 3600.0, 2700.0], [24, 3600.0, 3600.0]]
    U_inf = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
    I0 = [0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11, 0.11]
    print max_turbulence_one_angle(layout, U_inf, 0.0, I0, Jensen, thrust_coefficient, "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/windsim_ct.dat", frandsen2)
