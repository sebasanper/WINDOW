def total_costs(oandm_costs, support_structure_costs, infield_cable_costs, other_costs):
    from costs.investment_costs.management_cost import management_costs
    management_cost_support = management_costs(support_structure_costs + infield_cable_costs)
    return oandm_costs + management_cost_support + other_costs + infield_cable_costs

