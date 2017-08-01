central_platform = [[1000.0, 1000.0]]  # List with coordinates of electrical substations.
number_turbines_per_cable = [3]  # Maximum number of turbines connected per collection line.
NT = 9  # Number of turbines in wind farm.
cable_installation_cost = 365.0  # Cost of cable installation per metre.


class Cost1:
    def __init__(self, value, currency, year):
        global value_year
        # Inflation and exchange rate {'Currency Code': [Average inflation rate, Exchange rate to Euro]}
        self.conversion = {'USD': [2.57, 0.89],
                           'GBP': [2.55, 1.27],
                           'DKK': [1.84, 0.13],
                           'SEK': [2.03, 0.11],
                           'NOK': [1.95, 0.11],
                           'Euro': [2.16, 1.0]}

        inflation_rate = self.conversion[currency][0]
        exchange_rate = self.conversion[currency][1]

        self.ref_value = value
        self.currency = currency
        self.ref_year = year
        self.value = value * ((1.0 + (inflation_rate / 100.0)) ** (value_year - year)) * exchange_rate


def read_cablelist():
    cables_info = []
    with open("cable_list.dat",
              "r") as cables:
        next(cables)
        for line in cables:
            cols = line.split()
            cables_info.append([float(cols[0]), float(cols[1]), float(cols[2])])
    return cables_info

# Physical Environment
ref_height_wind_speed = 90.0
alpha = 0.10  # Approximate mean value of fits to data in ECN report and paper of Tambke (EWEC 2004)
hat = 0.8  # Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more than
#  half of this is taken for 'extrapolation'
lat = - 0.8  # Horns Rev website: Tides are approximately 1.2 m; Paper ICCE: appr. 1.5 m - A little more
# than half of this is taken for 'extrapolation'
storm_surge_pos = 2.5  # Paper ICCE
storm_surge_neg = - 0.5  # Guess
Hs_50_year = 5.0  # Horns Rev website: Highest value in graph of Hm0 is 4.3. Somewhat higher value taken for
# 'extrapolation' (note: graph is for 1 hour values) - Support structure design tool description derives Hs
# _1_year = 0.64 * Hs_50_year
Hs_1_year = 3.3  # Horns Rev website: waves of more than 6 m height reached every year. Divided by 1.86 to
# estimate significant wave height
current_depth_averaged_50_year = 0.8  # [m/s] Horns Rev website: Currents may reach 0.8 m/s during storms
# (doesn't mention return period and whether this is depth averaged)
angle_wave_current_50_year = 20.0  # [degrees] (Arbitrary default)
water_temperature = 15.0  # [degrees Celsius] 'Temperature-report' gives 17 degrees surface temp in August
#  and 'Temperature variation-report' gives variation of 2 degrees (highest temperature, so: August, is the worst case)
water_density = 1025.0  # [kg/m^3] Generic value
d50_soil = 0.0002  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2.
# in fish IEA report
d90_soil = 0.0005  # [m]  Values given as 'range' in baggrund8 IEA report and confirmed by figure 2.2.
# in fish IEA report
friction_angle = 35.0  # [degrees] Depth averaged friction angle from 'friction angle-report'
submerged_unit_weight = 10000.0  # [N/m^3] From 'friction angle-report', lighter layer ignored, because
# it is at great depth.

V_rated_voltage = [22000, 33000, 45000, 66000, 132000, 220000]  # Rated voltage in V # User's option

power_factor = 1.0  # cos angle
inflationrate = 1.18  # average inflation rate
exchangerate = 0.11  # exchange rate of SEK to Euros

# cost constants
Ap_init = [0.284, 0.411, 0.516, 0.688, 1.971, 3.181]  # must be multiplied by 10**6
Bp_init = [0.583, 0.596, 0.612, 0.625, 0.209, 0.11]  # must be multiplied by 10**6
Cp_init = [6.15, 4.1, 3.0, 2.05, 1.66, 1.16]  # must be multiplied by 10**6

# Cable procurement costs

rv = 1  # User can pick each time one rated voltage. 0 represents the first place in a Python list

# ------------- Cable Topology - INPUT ------------------
Crossing_penalty = 0
Area = []
# Transmission=[[central_platform_locations[0],[463000,5918000]],[central_platform_locations[1],[463000,5918000]]]
Transmission = []  # Two coordinates (starting, ending points) per transmission line.

# ---------------- LPC/Costs - INPUT ------------------------------------------
i = 0.1  # interest rate [-]
v = 0.025  # inflation rate [-]
operational_lifetime = 20  # [years] - FIXED VALUE NOTE: The fixed price in PPA is valid for a number of
# full load hours that is reached in appr. 10 years. After that, market prices apply.
value_year = 2016
actual_year = 2016  # Year for which costs are expressed
management_percentage = 3.0  # [%]
distance_to_grid = 55000.0  # [m] Grid connection report: Submarine cable length 21 km - Onshore cable
# length 34 km - Total 50 km
distance_to_harbour = 20000.0  # [m] Spare part optimisation report says the 20 km sail to Horns Rev
onshore_transport_distance = 100000.0  # [m]
frequency = 50  # [Hz]
transmission_voltage = 220000.0  # [V]
grid_coupling_point_voltage = 169000.0  # [V]
rho_copper = 8940  # [kg/m^3]
rho_xlpe = 940  # [kg/m^3]
epsilon_0 = 8.85e-12  # [F/m]
epsilon_r = 2.3  # [-] (XLPE)
