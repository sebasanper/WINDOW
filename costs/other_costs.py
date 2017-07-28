def other_costs(depth_central_platform, number_turbines, infield_length):
    from turbine_description import rated_power
    from costs.investment_costs.project_development_cost import project_development_cost
    from costs.investment_costs.management_cost import management_costs
    from costs.investment_costs.procurement_costs.auxiliary_costs.auxiliary_costs import auxiliary_procurement
    from costs.investment_costs.procurement_costs.electrical_system_costs.electrical_costs import electrical_procurement_costs
    from costs.investment_costs.procurement_costs.RNA_costs.RNA_costs import rna_costs
    from costs.investment_costs.installation_costs.auxiliary_installation_costs import auxiliary_installation_costs
    from costs.investment_costs.installation_costs.electrical_installation_costs import electrical_installation_costs
    from costs.investment_costs.installation_costs.RNA_installation_costs import rna_installation_costs
    from costs.OM_costs.om_models import oandm
    from costs.decommissioning_costs.decommissioning_costs import decommissioning_costs

    project_development = project_development_cost(number_turbines, rated_power)

    procurement_auxiliary = auxiliary_procurement(depth_central_platform)

    procurement_rna = rna_costs()

    procurement_electrical = electrical_procurement_costs()

    installation_auxiliary = auxiliary_installation_costs()

    installation_electrical = electrical_installation_costs()

    installation_rna = rna_installation_costs()

    decommissioning = decommissioning_costs(infield_length)

    investment_costs = project_development + procurement_auxiliary + procurement_rna + procurement_electrical + installation_auxiliary + installation_electrical + installation_rna

    # print "installation + procurement turbines"
    # print procurement_rna + installation_rna
    #
    # print "installation + procurement electrical"
    # print installation_electrical + procurement_electrical
    #
    # print "project development"
    # print project_development
    #
    # print "auxiliary costs"
    # print procurement_auxiliary + installation_auxiliary
    #
    # print "decommissioning costs"
    # print decommissioning

    management_investment = management_costs(investment_costs)

    # print "investment costs"
    # print investment_costs + management_investment

    return investment_costs + management_investment, decommissioning


if __name__ == '__main__':
    print total_costs(20.0, 5, 230000)
