class Workflow:
    def __init__(self, inflow_model, windrose_file, wake_turbulence_model, aeroloads_model, depth_model, support_design_model,
                 hydroloads_model, OandM_model, cable_costs_model, cable_efficiency_model, thrust_coefficient_model, thrust_lookup_file, wake_mean_model, wake_merging_model, power_model, power_lookup_file, aep_model, more_costs, total_costs_model,
                 finance_model):

        self.print_output = False
        self.draw_infield = False

        self.inflow_model = inflow_model
        self.wake_turbulence_model = wake_turbulence_model
        self.aeroloads_model = aeroloads_model
        self.depth_model = depth_model
        self.support_design_model = support_design_model
        self.hydroloads_model = hydroloads_model
        self.OandM_model = OandM_model
        self.cable_topology_model = cable_costs_model
        self.cable_efficiency_model = cable_efficiency_model
        self.thrust_coefficient_model = thrust_coefficient_model
        self.wake_mean_model = wake_mean_model
        self.wake_merging_model = wake_merging_model
        self.power_model = power_model
        self.aep_model = aep_model
        self.total_costs_model = total_costs_model
        self.finance_model = finance_model
        self.more_costs = more_costs
        self.windrose = self.inflow_model(windrose_file)
        self.thrust_lookup_file = thrust_lookup_file
        self.power_lookup_file = power_lookup_file

    # @profile
    def connect(self, turbine_coordinates):
        self.number_turbines = len(turbine_coordinates)
        # print turbine_coordinates
        self.minx = min([turbine[1] for turbine in turbine_coordinates])
        self.maxx = max([turbine[1] for turbine in turbine_coordinates])
        self.miny = min([turbine[2] for turbine in turbine_coordinates])
        self.maxy = max([turbine[2] for turbine in turbine_coordinates])
        from site_conditions.terrain.terrain_models import depth
        from farm_energy.wake_model_mean_new.wake_1angle import energy_one_angle
        from farm_energy.wake_model_mean_new.wake_1angle_turbulence import max_turbulence_one_angle
        from costs.investment_costs.BOS_cost.cable_cost.Hybrid import draw_cables
        from farm_description import central_platform, read_cablelist, number_turbines_per_cable
        from turbine_description import rated_current
        from site_conditions.wind_conditions.windrose import WeibullWindBins, MeanWind
        from farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen

        cables_info = read_cablelist()
        cable_list = []

        for number in number_turbines_per_cable:
            for cable in cables_info:
                if rated_current * number <= cable[1]:
                    cable_list.append([number, cable[2] + 365.0])
                    break

        # print cable_list

        from turbine_description import cutin_wind_speed, cutout_wind_speed

        if self.print_output is True: print "=== PREPARING WIND CONDITIONS ==="

        self.wind_directions, self.direction_probabilities = self.windrose.adapt_directions()

        if self.inflow_model == MeanWind:

            self.wind_speeds = self.windrose.expected_wind_speeds
            self.freestream_turbulence = [0.11]
            self.wind_speeds_probabilities = [[100.0] for _ in range(len(self.wind_directions))]

        elif self.inflow_model == WeibullWindBins:
            self.windrose.cutin = cutin_wind_speed
            self.windrose.cutout = cutout_wind_speed
            self.wind_speeds, self.wind_speeds_probabilities = self.windrose.speed_probabilities()
            self.freestream_turbulence = [0.11 for _ in range(len(self.wind_speeds[0]))]

        # if self.print_output is True: print self.wind_speeds, self.wind_speeds_probabilities

        if self.print_output is True: print "=== CALCULATING WATER DEPTH ==="
        self.water_depths = depth(turbine_coordinates, self.depth_model(self.minx, self.maxx, self.miny, self.maxy))
        if self.print_output is True: print str(self.water_depths) + "\n"

        central_platform_coordinates = [[0, central_platform[0][0], central_platform[0][1]]]
        if self.print_output is True: print "=== CALCULATING DEPTH AT CENTRAL PLATFORM ==="
        self.depth_central_platform = depth(central_platform_coordinates, self.depth_model(self.minx, self.maxx, self.miny, self.maxy))[0]
        if self.print_output is True: print str(self.depth_central_platform) + " m\n"

        if self.print_output is True: print "=== OPTIMISING INFIELD CABLE TOPOLOGY (COST)==="
        if self.draw_infield is True: draw_cables(turbine_coordinates, central_platform, cable_list)
        if self.cable_topology_model != "ConstantCable":
            self.cable_topology_costs, self.cable_topology, self.infield_length = self.cable_topology_model(turbine_coordinates)
        if self.cable_topology_model == "ConstantCable":
            self.cable_topology_costs = 9960476.0
            self.infield_length = 15276.0
        # print self.cable_topology
        if self.print_output is True: print str(self.cable_topology_costs) + " EUR\n" + str(self.infield_length)

        self.energies_per_angle = []
        self.turbulences_per_angle = []
        self.cable_efficiencies_per_angle = []
        self.array_efficiencies = []
        # if self.print_output is True: print [sum(self.wind_speeds_probabilities[i]) for i in range(len(self.wind_speeds_probabilities))]

        self.max_turbulence_per_turbine = [0.0 for _ in range(len(turbine_coordinates))]

        if self.print_output is True: print "=== CALCULATING ENERGY, TURBULENCE PER WIND DIRECTION ==="
        for i in range(len(self.wind_directions)):
            # print " === Wind direction = " + str(self.wind_directions[i])
            # if self.print_output is True: print self.wind_speeds_probabilities[i]
            self.aero_energy_one_angle, self.powers_one_angle = energy_one_angle(turbine_coordinates, self.wind_speeds[i], self.wind_speeds_probabilities[i], self.wind_directions[i], self.freestream_turbulence, self.wake_mean_model, self.power_model, self.power_lookup_file, self.thrust_coefficient_model, self.thrust_lookup_file, self.wake_merging_model)

            # if self.print_output is True: print self.aero_energy_one_angle
            # if self.print_output is True: print self.powers_one_angle, max(self.powers_one_angle)
            # if self.print_output is True: print turbine_coordinates, self.wind_speeds[i], self.wind_directions[i], self.freestream_turbulence[0], Jensen, self.thrust_coefficient_model, self.wake_turbulence_model
            if self.wake_turbulence_model != "ConstantTurbulence":
                self.turbulences = max_turbulence_one_angle(turbine_coordinates, self.wind_speeds[i], self.wind_directions[i], self.freestream_turbulence, Jensen, self.thrust_coefficient_model, self.thrust_lookup_file, self.wake_turbulence_model)
            if self.cable_topology_model != "ConstantCable":
                self.cable_topology_efficiency = self.cable_efficiency_model(self.cable_topology, turbine_coordinates, self.powers_one_angle)

            self.energy_one_angle_weighted = self.aero_energy_one_angle * self.direction_probabilities[i] / 100.0
            self.array_efficiency = (self.aero_energy_one_angle / (float(len(turbine_coordinates)) * max(self.powers_one_angle) * 8760.0))
            self.array_efficiencies_weighted = self.array_efficiency * self.direction_probabilities[i] / 100.0

            self.array_efficiencies.append(self.array_efficiencies_weighted)
            self.energies_per_angle.append(self.energy_one_angle_weighted)
            if self.wake_turbulence_model != "ConstantTurbulence":
                self.turbulences_per_angle.append(self.turbulences)
            if self.cable_topology_model != "ConstantCable":
                self.cable_efficiencies_per_angle.append(self.cable_topology_efficiency)

            if self.wake_turbulence_model != "ConstantTurbulence":
                for j in range(len(turbine_coordinates)):
                    if self.turbulences[j] > self.max_turbulence_per_turbine[j]:
                        self.max_turbulence_per_turbine[j] = self.turbulences[j]

        # if self.print_output is True: print self.array_efficiencies
        if self.print_output is True: print " --- Array efficiency---"
        self.array_efficiency = sum(self.array_efficiencies)
        if self.print_output is True: print str(self.array_efficiency * 100.0) + " %\n"

        if self.print_output is True: print " --- Farm annual energy without losses---"
        self.farm_annual_energy = sum(self.energies_per_angle)
        if self.print_output is True: print str(self.farm_annual_energy / 1000000.0) + " MWh\n"

        if self.print_output is True: print " --- Infield cable system efficiency ---"
        if self.cable_topology_model != "ConstantCable":
            self.cable_efficiency = sum(self.cable_efficiencies_per_angle) / len(self.cable_efficiencies_per_angle)  # TODO Check if average is the way to go instead of weighted average with probability of direction.
        if self.cable_topology_model == "ConstantCable":
            self.cable_efficiency = 0.99
        if self.print_output is True: print str(self.cable_efficiency * 100.0) + " %\n"

        if self.print_output is True: print " --- Maximum wind turbulence intensity ---"
        if self.wake_turbulence_model != "ConstantTurbulence":
            self.turbulence = self.max_turbulence_per_turbine
        elif self.wake_turbulence_model == "ConstantTurbulence":
            self.turbulence = [0.25 for _ in range(self.number_turbines)]
        if self.print_output is True: print str([self.turbulence[l] * 100.0 for l in range(len(self.turbulence))]) + " %\n"

        # --------- COSTS ----------------------------------------

        if self.print_output is True: print " --- Other investment and decommissioning costs ---"
        self.investment, self.decommissioning_cost = self.more_costs(self.depth_central_platform, self.number_turbines, self.infield_length)
        if self.print_output is True: print "Other investment costs"
        if self.print_output is True: print str(self.investment) + " EUR\n"
        if self.print_output is True: print "Decommissioning costs"
        if self.print_output is True: print str(self.decommissioning_cost) + " EUR\n"

        if self.print_output is True: print " --- Support structure investment costs ---"
        if self.support_design_model != "ConstantSupport":
            self.support_costs = self.support_design_model(self.water_depths, self.turbulence)
        elif self.support_design_model == "ConstantSupport":
            self.support_costs = 72376799.0
        if self.print_output is True: print str(self.support_costs) + " EUR\n"

        self.aeroloads = 0.0
        self.hydroloads = 0.0

        if self.print_output is True: print " --- O&M costs---"
        self.om_costs, self.availability = self.OandM_model(self.farm_annual_energy, self.aeroloads, self.hydroloads, turbine_coordinates)
        # self.om_costs *= 20.0  # Number of years
        if self.print_output is True: print self.om_costs
        if self.print_output is True: print str(self.om_costs) + " EUR\n"

        if self.print_output is True: print " --- Total energy production ---"
        self.aep = self.aep_model(self.farm_annual_energy, self.availability, self.cable_efficiency)
        if self.print_output is True: print str(self.aep / 1000000.0) + " MWh\n"

        if self.print_output is True: print " --- Total investment costs ---"
        self.total_costs = self.support_costs + self.cable_topology_costs + self.investment
        if self.print_output is True: print str(self.total_costs) + " EUR\n"

        if self.print_output is True: print " --- LPC ---"
        self.finance = self.finance_model(self.investment + self.cable_topology_costs + self.support_costs, self.om_costs, self.decommissioning_cost, self.farm_annual_energy, 0.95)
        if self.print_output is True: print str(self.finance) + " cents/kWh\n"

        return self.finance

    def run(self, layout_file):

        from farm_energy.layout.layout import read_layout
        from time import time
        from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power2, thrust_coefficient2, power, thrust_coefficient
        from farm_energy.wake_model_mean_new.ainslie1d import ainslie
        from farm_energy.wake_model_mean_new.ainslie2d import ainslie_full
        from farm_energy.wake_model_mean_new.jensen import determine_if_in_wake, wake_radius, wake_deficit
        from farm_energy.wake_model_mean_new.larsen import deff, wake_deficit_larsen, wake_radius, x0, rnb, r95, c1, determine_if_in_wake_larsen, wake_speed
        from farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, Quarton, danish_recommendation, frandsen, larsen_turbulence
        self.coordinates = read_layout(layout_file)
        start_time = time()
        answer = self.connect(self.coordinates)
        self.runtime = time() - start_time
        self.power_calls = power2.count()
        self.thrust_calls = thrust_coefficient2.count()
        power.reset()
        thrust_coefficient.reset()
        ainslie.reset()
        ainslie_full.reset()
        determine_if_in_wake.reset()
        wake_radius.reset()
        wake_deficit.reset()
        frandsen2.reset()
        Quarton.reset()
        danish_recommendation.reset()
        larsen_turbulence.reset()
        frandsen.reset()
        return answer


if __name__ == '__main__':
    from site_conditions.wind_conditions.windrose import MeanWind, WeibullWindBins
    from costs.investment_costs.BOS_cost.cable_cost.cable_cost_models import cable_optimiser, radial_cable, random_cable
    from costs.investment_costs.BOS_cost.cable_cost.cable_efficiency import infield_efficiency
    from costs.OM_costs.om_models import oandm
    from costs.investment_costs.BOS_cost.support_cost.farm_support_cost import farm_support_cost
    from finance.finance_models import LPC
    from farm_energy.AEP.aep import aep_average
    from costs.other_costs import other_costs
    from costs.total_costs import total_costs
    # from farm_energy.wake_model_mean_new.aero_power_ct_models.thrust_coefficient import ct_v80
    from farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, danish_recommendation, frandsen, \
        larsen_turbulence, Quarton
    from site_conditions.terrain.terrain_models import Flat, Plane, Rough, Gaussian
    from farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen, LarsenEffects as Larsen, Ainslie1DEffects as Ainslie1D, Ainslie2DEffects as Ainslie2D, constantwake
    from farm_energy.wake_model_mean_new.wake_overlap import root_sum_square, maximum, multiplied, summed
    from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power, thrust_coefficient, power2, thrust_coefficient2

    from time import time

    # @profile
    def exe():
        start = time()
        workflow1 = Workflow(MeanWind, "/home/sebasanper/PycharmProjects/owf_MDAO/site_conditions/wind_conditions/weibull_windrose.dat", frandsen2, None, Flat, farm_support_cost, None, oandm, cable_optimiser, infield_efficiency, thrust_coefficient, "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/windsim_ct.dat", Jensen, root_sum_square, power, "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/nrel_cp.dat", aep_average, other_costs, total_costs, LPC)
        # workflow1.windrose.nbins = 15
        workflow1.print_output = True
        print workflow1.run("layout_creator/random_layout1.dat")
        runtime = time() - start
        print "////  time Jensen : " + str(runtime) + " s."

    # a
    wakemodels = [constantwake, Jensen, Larsen, Ainslie1D, Ainslie2D]
    # i
    weibullmodels = [MeanWind, WeibullWindBins]
    # b
    windrosemodels = [
        "/home/sebasanper/PycharmProjects/owf_MDAO/site_conditions/wind_conditions/windrose.dat",
        "/home/sebasanper/PycharmProjects/owf_MDAO/site_conditions/wind_conditions/weibull_windrose_12sameWeibull.dat",
        "/home/sebasanper/PycharmProjects/owf_MDAO/site_conditions/wind_conditions/weibull_windrose_12identical.dat"]
    # c
    turbmodels = ["ConstantTurbulence", frandsen2, danish_recommendation, frandsen, larsen_turbulence, Quarton]
    # d
    cablemodels = ["ConstantCable", cable_optimiser, radial_cable, random_cable]
    # e
    mergingmodels = [root_sum_square, maximum, multiplied, summed]
    # f
    thrustmodels = ["/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/ConstantThrust.dat", "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/windsim_ct.dat", "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/NREL_5MW_C_T_new.txt", "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/ct_curve.dat"]
    # g
    powermodels = ["/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/ConstantPower.dat", "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/power_curve.dat", "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/windsim_power.dat", "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/powercurve.dat", "/home/sebasanper/PycharmProjects/owf_MDAO/farm_energy/wake_model_mean_new/aero_power_ct_models/nrel_cp.dat"]
    # h
    depthmodels = [Flat, Gaussian, Plane, Rough]
    # j
    farm_support_cost_models = ["ConstantSupport", farm_support_cost]

    def study(a, b, c, d, e, f, g, h, i, j, nbins, layout_input_file, output):
        # print a, b, c, d, e, f, g, h, i
        workflow1 = Workflow(weibullmodels[i], windrosemodels[b], turbmodels[c], None, depthmodels[h], farm_support_cost_models[j], None, oandm, cablemodels[d], infield_efficiency, thrust_coefficient, thrustmodels[f], wakemodels[a], mergingmodels[e], power, powermodels[g], aep_average, other_costs, total_costs, LPC)
        start = time()
        workflow1.windrose.nbins = nbins
        workflow1.print_output = True
        workflow1.run(layout_input_file)
        runtime = time() - start
        output.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(a, b, c, d, e, f, g, h, i, j, workflow1.aep, workflow1.finance, runtime, workflow1.power_calls, workflow1.thrust_calls))
        return workflow1.aep, workflow1.finance, runtime

    def test_study(nbins, layout_input_file, output_file):
        start1 = time()
        with open(output_file, "a", 1) as output:
            study(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, nbins, layout_input_file, output)

        print time() - start1

    test_study(15, "layout.dat", "test.dat")
    # pass
