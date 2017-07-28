from turbine_description import purchase_price, warranty_percentage
from farm_description import NT


def rna_costs():

    # Investment costs - Procurement - Rotor/nacelle
    inv_procurement_turbines_purchase = NT * purchase_price
    inv_procurement_turbines_warranty = (warranty_percentage / 100.0) * inv_procurement_turbines_purchase

    total_rna_cost = inv_procurement_turbines_purchase + inv_procurement_turbines_warranty

    return total_rna_cost

if __name__ == '__main__':
    print rna_costs()
