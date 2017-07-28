from math import sqrt

voltage = 33000.0
rated_power = 5000000.0
rated_current = rated_power / (sqrt(3) * voltage)  # A = Power / sqrt(3) / Voltage. 3 phase.
cutin_wind_speed = 3.0
cutout_wind_speed = 25.0

hub_height = 90.0
solidity_rotor = 0.0516  # [-] 'Generic' value, based on Peter Jamieson's book - Figure 2.5 - P.53
cd_rotor_idle_vane = 0.4  # [-] 'Generic' value, very dependent on angle of attack and therefore the assumed rotor misalignment
# cd_rotor_idle_failed_pitch = 1.2 # [-]
cd_nacelle = 1.2  # [-] OWTES V66: 1.3, but using a frontal area of 13 m^2
front_area_nacelle = 14.0  # [m^2] Vestas V80 brochure: height for transport 4 m, width 3.4 m, rounded up 14 m^2 to include height including cooler top 5.4 m
max_thrust = 1185900.0  # [N] Maximum thrust determined from thrust coefficient curve multiplied with 1.5 amplification factor (determined by Otto for NREL 5 MW turbine)
yaw_to_hub_height = 5.01  # [m]
mass = 350000.0  # [kg] 296,780 kg nacelle + 3x 17.74 ton blades
mass_eccentricity = 1.9  # [m] - in x-direction, so negative when upwind of tower centre
yaw_diameter = 3.87  # [m]
rotor_radius = 63.0  # [m]
wind_speed_at_max_thrust = 11.4  # [m/s]
generator_voltage = 690.0  # [V] There are 480 and 690 voltage versions of the V80. The higher voltage is assumed, considering the need of high voltage in the connections to the public grid.
purchase_price = 5850000.0  # [Euro]
warranty_percentage = 15.0  # [%]
