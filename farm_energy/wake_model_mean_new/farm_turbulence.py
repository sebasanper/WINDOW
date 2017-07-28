from wake_1angle_turbulence import turbulence_one_angle
from aero_power_ct_models.thrust_coefficient import v80
from downstream_effects import JensenEffects as Jensen

layout = [[0, 500.0, 0.0], [1, 1000.0, 0.0], [2, 1500.0, 0.0], [3, 2000.0, 0.0], [4, 2500.0, 0.0], [5, 3000.0, 0.0]]
U_inf = 8.5
I0 = 0.08
angle = 180.0

print turbulence_one_angle(layout, U_inf, angle, I0, Jensen, v80)
