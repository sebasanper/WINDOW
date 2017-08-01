class Workflow:
    def __init__(self, inflow_model, windrose_file, wake_turbulence_model, aeroloads_model, depth_model,
                 support_design_model,
                 hydroloads_model, OandM_model, cable_costs_model, cable_efficiency_model, thrust_coefficient_model,
                 thrust_lookup_file, wake_mean_model, wake_merging_model, power_model, power_lookup_file, aep_model,
                 more_costs, total_costs_model,
                 finance_model):
        self.print_output = False
        self.draw_infield = False
        self.number_turbines = 0
        self.minx = 0
        self.maxx = 0
        self.miny = 0
        self.maxy = 0
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
        self.wind_directions = []
        self.direction_probabilities = []
        self.wind_speeds = []
        self.wind_speeds_probabilities = []
        self.freestream_turbulence = []
        self.water_depths = []
        self.depth_central_platform = []
        self.cable_topology = []
        self.cable_topology_costs = 0
        self.infield_length = 0
        self.energies_per_angle = []
        self.turbulences_per_angle = []
        self.cable_efficiencies_per_angle = []
        self.array_efficiencies = []
        self.max_turbulence_per_turbine = []
        self.aero_energy_one_angle = []
        self.powers_one_angle = []
        self.cable_topology_efficiency = 0
        self.energy_one_angle_weighted = 0
        self.turbulences = []
        self.array_efficiency = []
        self.array_efficiencies_weighted = []
        self.farm_annual_energy = 0
        self.cable_efficiency = 0
        self.turbulence = []
        self.investment = 0
        self.decommissioning_cost = 0
        self.aeroloads = 0.0
        self.hydroloads = 0.0
        self.support_costs = 0
        self.om_costs = 0
        self.availability = 0
        self.aep = 0
        self.total_costs = 0
        self.finance = 0
        self.coordinates = []
        self.runtime = 0
        self.power_calls = 0
        self.thrust_calls = 0

        # @profile
    def connect(self, turbine_coordinates):
        self.number_turbines = len(turbine_coordinates)
        self.minx = min([turbine[1] for turbine in turbine_coordinates])
        self.maxx = max([turbine[1] for turbine in turbine_coordinates])
        self.miny = min([turbine[2] for turbine in turbine_coordinates])
        self.maxy = max([turbine[2] for turbine in turbine_coordinates])
        from site_conditions.terrain.terrain_models import depth
        from farm_energy.wake_model_mean_new.wake_1angle import energy_one_angle
        from farm_energy.wake_model_mean_new.wake_1angle_turbulence import max_turbulence_one_angle
        from costs.investment_costs.BOS_cost.cable_cost.Hybrid import draw_cables
        from farm_description import central_platform, read_cablelist, number_turbines_per_cable, cable_installation_cost
        from turbine_description import rated_current
        from site_conditions.wind_conditions.windrose import WeibullWindBins, MeanWind
        from farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen

        cables_info = read_cablelist()
        cable_list = []
        for number in number_turbines_per_cable:
            for cable in cables_info:
                if rated_current * number <= cable[1]:
                    cable_list.append([number, cable[2] + cable_installation_cost])  # 365 is cable installation cost per linear metre.
                    break
        from turbine_description import cutin_wind_speed, cutout_wind_speed
        if self.print_output:
            print "=== PREPARING WIND CONDITIONS ==="
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
        if self.print_output:
            print "=== CALCULATING WATER DEPTH ==="
        self.water_depths = depth(turbine_coordinates, self.depth_model(self.minx, self.maxx, self.miny, self.maxy))
        if self.print_output:
            print str(self.water_depths) + "\n"
        central_platform_coordinates = [[0, central_platform[0][0], central_platform[0][1]]]
        if self.print_output:
            print "=== CALCULATING DEPTH AT CENTRAL PLATFORM ==="
        self.depth_central_platform = \
            depth(central_platform_coordinates, self.depth_model(self.minx, self.maxx, self.miny, self.maxy))[0]
        if self.print_output:
            print str(self.depth_central_platform) + " m\n"
        if self.print_output:
            print "=== OPTIMISING INFIELD CABLE TOPOLOGY (COST)==="
        if self.draw_infield:
            draw_cables(turbine_coordinates, central_platform, cable_list)
        if self.cable_topology_model != "ConstantCable":
            self.cable_topology_costs, self.cable_topology, self.infield_length = self.cable_topology_model(
                turbine_coordinates)
        if self.cable_topology_model == "ConstantCable":
            self.cable_topology_costs = 9960476.0
            self.infield_length = 15276.0
        if self.print_output:
            print str(self.cable_topology_costs) + " EUR\n" + str(self.infield_length)
        self.max_turbulence_per_turbine = [0.0 for _ in range(len(turbine_coordinates))]
        if self.print_output:
            print "=== CALCULATING ENERGY, TURBULENCE PER WIND DIRECTION ==="
        for i in range(len(self.wind_directions)):
            # print " === Wind direction = " + str(self.wind_directions[i])
            self.aero_energy_one_angle, self.powers_one_angle = energy_one_angle(turbine_coordinates,
                                                                                 self.wind_speeds[i],
                                                                                 self.wind_speeds_probabilities[i],
                                                                                 self.wind_directions[i],
                                                                                 self.freestream_turbulence,
                                                                                 self.wake_mean_model, self.power_model,
                                                                                 self.power_lookup_file,
                                                                                 self.thrust_coefficient_model,
                                                                                 self.thrust_lookup_file,
                                                                                 self.wake_merging_model)
            if self.wake_turbulence_model != "ConstantTurbulence":
                self.turbulences = max_turbulence_one_angle(turbine_coordinates, self.wind_speeds[i],
                                                            self.wind_directions[i], self.freestream_turbulence, Jensen,
                                                            self.thrust_coefficient_model, self.thrust_lookup_file,
                                                            self.wake_turbulence_model)
            if self.cable_topology_model != "ConstantCable":
                self.cable_topology_efficiency = self.cable_efficiency_model(self.cable_topology, turbine_coordinates,
                                                                             self.powers_one_angle)
            self.energy_one_angle_weighted = self.aero_energy_one_angle * self.direction_probabilities[i] / 100.0
            self.array_efficiency = (
                self.aero_energy_one_angle / (float(len(turbine_coordinates)) * max(self.powers_one_angle) * 8760.0))
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
        if self.print_output:
            print " --- Array efficiency---"
        self.array_efficiency = sum(self.array_efficiencies)
        if self.print_output:
            print str(self.array_efficiency * 100.0) + " %\n"
        if self.print_output:
            print " --- Farm annual energy without losses---"
        self.farm_annual_energy = sum(self.energies_per_angle)
        if self.print_output:
            print str(self.farm_annual_energy / 1000000.0) + " MWh\n"
        if self.print_output:
            print " --- Infield cable system efficiency ---"
        if self.cable_topology_model != "ConstantCable":
            self.cable_efficiency = sum(self.cable_efficiencies_per_angle) / len(
                self.cable_efficiencies_per_angle)  # TODO Check if average is the way to go instead of weighted average
        # with probability of direction.
        if self.cable_topology_model == "ConstantCable":
            self.cable_efficiency = 0.99
        if self.print_output:
            print str(self.cable_efficiency * 100.0) + " %\n"
        if self.print_output:
            print " --- Maximum wind turbulence intensity ---"
        if self.wake_turbulence_model != "ConstantTurbulence":
            self.turbulence = self.max_turbulence_per_turbine
        elif self.wake_turbulence_model == "ConstantTurbulence":
            self.turbulence = [0.25 for _ in range(self.number_turbines)]
        if self.print_output:
            print str([self.turbulence[l] * 100.0 for l in range(len(self.turbulence))]) + " %\n"
        # --------- COSTS ----------------------------------------
        if self.print_output:
            print " --- Other investment and decommissioning costs ---"
        self.investment, self.decommissioning_cost = self.more_costs(self.depth_central_platform, self.number_turbines,
                                                                     self.infield_length)
        if self.print_output:
            print "Other investment costs"
        if self.print_output:
            print str(self.investment) + " EUR\n"
        if self.print_output:
            print "Decommissioning costs"
        if self.print_output:
            print str(self.decommissioning_cost) + " EUR\n"
        if self.print_output:
            print " --- Support structure investment costs ---"
        if self.support_design_model != "ConstantSupport":
            self.support_costs = self.support_design_model(self.water_depths, self.turbulence)
        elif self.support_design_model == "ConstantSupport":
            self.support_costs = 72376799.0
        if self.print_output:
            print str(self.support_costs) + " EUR\n"
        if self.print_output:
            print " --- O&M costs---"
        self.om_costs, self.availability = self.OandM_model(self.farm_annual_energy, self.aeroloads, self.hydroloads,
                                                            turbine_coordinates)
        if self.print_output:
            print self.om_costs
        if self.print_output:
            print str(self.om_costs) + " EUR\n"
        if self.print_output:
            print " --- Total energy production ---"
        self.aep = self.aep_model(self.farm_annual_energy, self.availability, self.cable_efficiency)
        if self.print_output:
            print str(self.aep / 1000000.0) + " MWh\n"
        if self.print_output:
            print " --- Total investment costs ---"
        self.total_costs = self.support_costs + self.cable_topology_costs + self.investment
        if self.print_output:
            print str(self.total_costs) + " EUR\n"
        if self.print_output:
            print " --- LPC ---"
        self.finance = self.finance_model(self.investment + self.cable_topology_costs + self.support_costs,
                                          self.om_costs, self.decommissioning_cost, self.farm_annual_energy, 0.95)
        if self.print_output:
            print str(self.finance) + " cents/kWh\n"
        return self.finance

    def run(self, layout_file):
        from farm_energy.layout.layout import read_layout
        from time import time
        from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power2, thrust_coefficient2, \
            power, thrust_coefficient
        from farm_energy.wake_model_mean_new.ainslie1d import ainslie
        from farm_energy.wake_model_mean_new.ainslie2d import ainslie_full
        from farm_energy.wake_model_mean_new.jensen import determine_if_in_wake, wake_deficit
        from farm_energy.wake_model_mean_new.larsen import wake_radius
        from farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, Quarton, danish_recommendation, \
            frandsen, larsen_turbulence
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
