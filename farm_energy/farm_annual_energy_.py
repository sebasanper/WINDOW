from joblib import Parallel, delayed
from wake_model_mean_new.wake_1angle import energy_one_angle


def energy_all_directions_parallel(layout, wind_directions, probabilities_direction, freestream_wind_speeds, probabilities_speed, ambient_turbulences, WakeModel, PowerModel, ThrustModel, MergingModel):
    energy_per_direction = Parallel(n_jobs=-1)(delayed(energy_one_angle)(layout, freestream_wind_speeds, probabilities_speed[i], wind_directions[i], ambient_turbulences, WakeModel, PowerModel, ThrustModel, MergingModel) for i in range(len(wind_directions)))
    # print energy_per_direction
    total_energy = sum([energy_per_direction[i] * probabilities_direction[i] for i in range(len(energy_per_direction))])
    return total_energy


# def power_all_directions(layout, wind_directions, wake_model, powermodel):
#     powers = []
#     for angle in wind_directions:
#         fun = Wake1Angle(wake_model)
#         a = fun.wake_one_angle(layout, freestream_wind_speed=U0, wind_angle=angle, ambient_turbulence=I0)
#         b = plantpower(a, powermodel)
#         powers.append(b)
#     return powers


# def farm_annual_energy(probabilities_direction, energy_per_direction):
#     annual_energy = 0.0
#     for prob in range(len(probabilities_direction)):
#         annual_energy += probabilities_direction[prob] / 100.0 * 8760.0 * energy_per_direction[prob]
#     return annual_energy


if __name__ == '__main__':
    from wake_model_mean_new.aero_power_ct_models.aero_models import power_v80
    from plant_power_1angle import plantpower
    from wake_model_mean_new.downstream_effects import LarsenEffects as Larsen
    from wake_model_mean_new.wake_overlap import root_sum_square
    from wake_model_mean_new.aero_power_ct_models.thrust_coefficient import v80
    from layout.layout import read_layout
    # print wind_directions

    layout = read_layout("layout/coordinates.dat")
    directions = [0.0, 30.0, 60.0, 90.0]
    probabilities_dir = [25.0, 25.0, 25.0, 25.0]
    wind_speeds = [8.5]
    speed_prob = [[100.0], [100.0], [100.0], [100.0]]
    turbulences = [0.08]

    print energy_all_directions_parallel(layout, directions, probabilities_dir, wind_speeds, speed_prob, turbulences, Larsen, power_v80, v80, root_sum_square)
