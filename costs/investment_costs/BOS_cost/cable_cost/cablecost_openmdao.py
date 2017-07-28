from openmdao.api import Component, Group, Problem
# TODO


class CableCost(Component):
    def __init__(self):
        super(CableCost, self).__init__()

        self.add_param("x", val=0.0)
        self.add_param("y", val=0.0)

        self.add_output("cost", val=0.0)

    def solve_nonlinear(self, params, unknowns, resids):
        cost_per_meter = 200.0
        unknowns["cost"] = params["total_distance"] * cost_per_meter

if __name__ == '__main__':
    root = Group()
    root.add('cable_model', CableCost())

    top = Problem(root)
    top.setup()
    top["cable_model.total_distance"] = 23.0

    top.run()
    print top["cable_model.cost"]