from costs.investment_costs.BOS_cost.support_cost.lib.designers_support.dimension_team_support import DimensionTeamSupport
from costs.investment_costs.BOS_cost.support_cost.lib.system.properties import RNA
from costs.investment_costs.BOS_cost.support_cost.lib.environment.physical_environment import Site
from costs.currency import Cost1


def design_support(water_depth, TI):
    dimension_team_support = DimensionTeamSupport()
    dimension_team_support.fsf = TI + 1.0
    # dimension_team_support.fsf = 1.5
    rna = RNA()
    site_data = Site()
    site_data.water_depth = water_depth

    # print site_data.water_depth
    dimension_team_support.run(rna, site_data)

    boat_landing_cost = Cost1(60000.0, 'USD', 2003)  # [$/turbine]
    # Investment costs - Procurement & Installation - Support structure

    return dimension_team_support.total_support_structure_cost + boat_landing_cost


if __name__ == '__main__':
    print design_support(water_depth=12.0, TI=0.9)
