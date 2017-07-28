from farm_energy.wake_model_mean_new.aero_power_ct_models.util import interpolate
from numpy import pi
from memoize import Memoize
from turbine_description import cutout_wind_speed, cutin_wind_speed, rotor_radius, wind_speed_at_max_thrust as rated_wind, rated_power


class AeroLookup:

    def __init__(self, file_in):

        with open(file_in, "r") as data:
            self.x = []
            self.y = []
            for line in data:
                col = line.split()
                self.x.append(float(col[0]))
                self.y.append(float(col[1]))

    def interpolation(self, value):
        ii = 0
        lower = []
        upper = []
        if value <= self.x[0]:
            result = self.y[0]
        elif value < self.x[-1]:
            for x in self.x:
                if x <= value:
                    lower = [x, self.y[ii]]
                else:
                    upper = [x, self.y[ii]]
                    break
                ii += 1
            result = interpolate(float(lower[0]), float(lower[1]), float(upper[0]), float(upper[1]), value)
        else:
            result = self.y[-1]
        return result


def power_coefficient(wind_speed, rated, r, cutin=cutin_wind_speed, cutout=cutout_wind_speed):
    table_cp = AeroLookup("/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/nrel_cp.dat")
    if wind_speed < cutin:
        return 0.0
    elif wind_speed <= rated:
        cp = table_cp.interpolation(wind_speed)
        return 0.5 * 1.225 * pi * r ** 2.0 * wind_speed ** 3.0 * cp
    elif wind_speed <= cutout:
        return rated_power
    else:
        return 0.0


power_coefficient = Memoize(power_coefficient)

from memoize import countcalls
@countcalls
def power2(wind_speed, power_lookup_file, cutin=cutin_wind_speed, cutout=cutout_wind_speed, rated=rated_wind, r=rotor_radius):
    table_power = AeroLookup(power_lookup_file)
    # print "iuno"
    if power_lookup_file == "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/nrel_cp.dat":
        if wind_speed < cutin:
            return 0.0
        elif wind_speed <= rated:
            cp = table_power.interpolation(wind_speed)
            return 0.5 * 1.225 * pi * r ** 2.0 * wind_speed ** 3.0 * cp
        elif wind_speed <= cutout:
            return rated_power
        else:
            return 0.0

    if wind_speed < cutin:
        return 0.0
    elif wind_speed <= cutout:
        p = table_power.interpolation(wind_speed)
        return p
    else:
        return 0.0


power = Memoize(power2)


def thrust_nrel2(wind_speed, r=rotor_radius):
    table_thrust = AeroLookup("/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/nrel_ct.dat")
    if wind_speed < table_thrust.x[0]:
        T = table_thrust.y[0]
    elif wind_speed > table_thrust.x[-1]:
        T = table_thrust.x[-1]
    else:
        T = table_thrust.interpolation(wind_speed)
    ct = 1000.0 * T / (0.5 * 1.225 * pi * r ** 2.0 * wind_speed ** 2.0)
    if ct > 1.0:
        return 1.0
    else:
        return ct


thrust_nrel2 = Memoize(thrust_nrel2)

@countcalls
def thrust_coefficient2(wind_speed, lookup_file):
    # print "dos"
    ct_table = AeroLookup(lookup_file)
    ct = ct_table.interpolation(wind_speed)
    if ct > 0.9:
        ct = 0.9
    elif ct < 0.05:
        ct = 0.05
    return ct


thrust_coefficient = Memoize(thrust_coefficient2)


def power_v80(u0):
    if u0 < 4.0:
        return 0.0
    elif u0 <= 10.0:
        return (3.234808e-4 * u0 ** 7.0 - 0.0331940121 * u0 ** 6.0 + 1.3883148012 * u0 ** 5.0 - 30.3162345004 * u0 ** 4.0 + 367.6835557011 * u0 ** 3.0 - 2441.6860655008 * u0 ** 2.0 + 8345.6777042343 * u0 - 11352.9366182805) * 1000.0
    elif u0 <= 25.0:
        return 2000000.0
    else:
        return 0.0


power_v80 = Memoize(power_v80)

if __name__ == '__main__':
    table1 = AeroLookup("./nrel_cp.dat")
    # for v in range(1, 50):
    #     print v / 2.0, power_coefficient(v / 2.0, 64.0), thrust(v / 2.0, 64.0)
    print power_coefficient(25.0)
