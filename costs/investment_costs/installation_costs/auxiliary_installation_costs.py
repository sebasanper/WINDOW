from costs.currency import Cost1
from turbine_description import rated_power as P_rated
from farm_description import NT


def auxiliary_installation_costs():
    # Installation - Auxiliary
    harbour_per_watt = Cost1(0.02, 'USD', 2002)  # [$/Watt]
    measuring_tower_installation_costs = Cost1(550000.0, 'Euro', 2003)  # [Euro]

    # Investment costs - Installation - Auxiliary
    inv_installation_auxiliary_harbour = NT * P_rated * harbour_per_watt
    inv_installation_auxiliary_measuring_tower = measuring_tower_installation_costs

    total_aux_installation = inv_installation_auxiliary_harbour + inv_installation_auxiliary_measuring_tower

    return total_aux_installation

if __name__ == '__main__':
    print auxiliary_installation_costs()