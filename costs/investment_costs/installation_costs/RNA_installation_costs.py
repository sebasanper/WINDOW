from turbine_description import rotor_radius, hub_height
from costs.currency import Cost1
from farm_description import onshore_transport_distance, NT


def rna_installation_costs():
    r0 = rotor_radius
    # Installation - Rotor-nacelle assembly
    onshore_transport_coef_a = Cost1(5.84e-3, 'Euro', 2001)  # [Euro]
    onshore_transport_coef_b = Cost1(0.4, 'Euro', 2001)  # [Euro]
    onshore_transport_coef_c = Cost1(0.486, 'Euro', 2001)  # [Euro]
    onshore_transport_exp = 2.64
    turbine_installation_per_turbine_coef_a = Cost1(3.4e3, 'USD', 2010)  # [$/(m * turbine)]
    turbine_installation_per_turbine_coef_b = 50.0  # [m]

    # Investment costs - Installation - Rotor-nacelle assembly
    diameter = 2.0 * r0
    transport_per_turbine = ((onshore_transport_coef_a * diameter +
                              onshore_transport_coef_b) * onshore_transport_distance +
                             onshore_transport_coef_c * diameter ** onshore_transport_exp)

    inv_installation_turbines_onshore_transport = NT * transport_per_turbine
    inv_installation_turbines_offshore_works = (NT * turbine_installation_per_turbine_coef_a * (hub_height + turbine_installation_per_turbine_coef_b))
    
    total_rna_installation = inv_installation_turbines_offshore_works + inv_installation_turbines_onshore_transport

    return total_rna_installation

if __name__ == '__main__':
    print rna_installation_costs()
