from costs.currency import Cost1
from farm_description import NT
from turbine_description import rated_power as P_rated


def auxiliary_procurement(depth_central_platform):
    # Procurement-Auxiliary
    measuring_tower_costs = Cost1(2050000.0, 'Euro', 2003)  # [Euro]
    onshore_premises_costs = Cost1(1500000.0, 'Euro', 2003)  # [Euro]
    central_platform_modesty_factor = 2.0 / 3.0  # Introduced because the cost model was for a sophisticated platform that didn't match realised platforms
    central_platform_coef_a = Cost1(0.4e-3, 'SEK', 2003)  # [SEK/kg^2]
    central_platform_coef_b = Cost1(-50.0, 'SEK', 2003)  # [SEK/kg]
    central_platform_coef_c = Cost1(-80.0e6, 'SEK', 2003)  # [SEK]
    jacket_mass_coef_a = 582.0
    jacket_mass_exp_a = 0.19
    jacket_mass_exp_b = 0.48
    topside_mass_coef_a = 3.0e-3
    topside_mass_coef_b = 0.5e6
    
    # # Investment costs - Procurement - Auxiliary
    topside_mass = (topside_mass_coef_a * NT * P_rated + topside_mass_coef_b)
    mass_jacket = (jacket_mass_coef_a * depth_central_platform ** jacket_mass_exp_a * topside_mass ** jacket_mass_exp_b)
    inv_procurement_auxiliary_measuring_tower = measuring_tower_costs
    inv_procurement_auxiliary_onshore_premises = onshore_premises_costs
    inv_procurement_auxiliary_offshore_platform = central_platform_modesty_factor * (central_platform_coef_a * mass_jacket ** 2.0 + central_platform_coef_b * mass_jacket + central_platform_coef_c)

    total_auxiliary_procurement = inv_procurement_auxiliary_measuring_tower + inv_procurement_auxiliary_offshore_platform + inv_procurement_auxiliary_onshore_premises

    return total_auxiliary_procurement

if __name__ == '__main__':
    print auxiliary_procurement(25)
