import os
input_folder = 'Project1'
with open("turbine_description.py", "w") as out:
    out.write("from input_folder." + input_folder + ".turbine_description_5MW import *")
with open("farm_description.py", "w") as out:
    out.write("from input_folder." + input_folder + ".farm_description_5MW import *")
project_folder = os.path.join('input_folder', input_folder)
os.chdir(project_folder)
from workflow import Workflow
from site_conditions.wind_conditions.windrose import MeanWind, WeibullWindBins
from costs.investment_costs.BOS_cost.cable_cost.cable_cost_models import cable_optimiser, radial_cable, random_cable
from costs.investment_costs.BOS_cost.cable_cost.cable_efficiency import infield_efficiency
from costs.OM_costs.om_models import oandm
from costs.investment_costs.BOS_cost.support_cost.farm_support_cost import farm_support_cost
from finance.finance_models import LPC
from farm_energy.AEP.aep import aep_average
from costs.other_costs import other_costs
from costs.total_costs import total_costs
from farm_energy.wake_model_mean_new.wake_turbulence_models import frandsen2, danish_recommendation, frandsen, \
    larsen_turbulence, Quarton
from site_conditions.terrain.terrain_models import Flat, Plane, Rough, Gaussian
from farm_energy.wake_model_mean_new.downstream_effects import JensenEffects as Jensen, LarsenEffects as Larsen, \
    Ainslie1DEffects as Ainslie1D, Ainslie2DEffects as Ainslie2D, constantwake
from farm_energy.wake_model_mean_new.wake_overlap import root_sum_square, maximum, multiplied, summed
from farm_energy.wake_model_mean_new.aero_power_ct_models.aero_models import power, thrust_coefficient, power2, \
    thrust_coefficient2
from time import time

wakemodels = [constantwake, Jensen, Larsen, Ainslie1D, Ainslie2D]  # a - 1
windrosemodels = ["windrose.dat"]  # b - 2
turbmodels = ["ConstantTurbulence", frandsen2, danish_recommendation, frandsen, larsen_turbulence, Quarton]  # c - 3
cablemodels = ["ConstantCable", cable_optimiser, radial_cable, random_cable]  # d - 4
mergingmodels = [root_sum_square, maximum, multiplied, summed]  # e - 5
thrustmodels = ["farm_energy/wake_model_mean_new/aero_power_ct_models/ConstantThrust.dat", "ct_curve.dat"]  # f - 6
powermodels = ["farm_energy/wake_model_mean_new/aero_power_ct_models/ConstantPower.dat", "power_curve.dat"]  # g - 7
depthmodels = [Flat, Gaussian, Plane, Rough]  # h - 8
weibullmodels = [MeanWind, WeibullWindBins]  # i - 9
farm_support_cost_models = ["ConstantSupport", farm_support_cost]  # j - 10


def run_workflow(a, b, c, d, e, f, g, h, i, j):
    workflow1 = Workflow(weibullmodels[i], windrosemodels[b], turbmodels[c], None, depthmodels[h],
                         farm_support_cost_models[j], None, oandm, cablemodels[d], infield_efficiency,
                         thrust_coefficient, thrustmodels[f], wakemodels[a], mergingmodels[e], power,
                         powermodels[g], aep_average, other_costs, total_costs, LPC)
    nbins = 17  # Number of wind speeds bins for the discretisation of the Weibull distribution.
    real_angle = 30.0  # Angle [degrees] per wind sector in measured windrose.
    artif_angle = 1.0  # Desired angle [degrees] resolution for wake analysis.
    workflow1.windrose.nbins = nbins
    workflow1.windrose.artificial_angle = artif_angle
    workflow1.windrose.real_angle = real_angle
    workflow1.print_output = True
    start1 = time()
    workflow1.run("layout.dat")
    print time() - start1, "seconds runtime"
    power2.reset()
    thrust_coefficient2.reset()

    with open("output.dat", "a", 1) as output2:
        output2.write("{}\t{}\t{}\n".format(workflow1.aep, workflow1.finance, workflow1.runtime))

if __name__ == '__main__':
    run_workflow(1, 0, 1, 1, 0, 1, 1, 3, 1, 1)
