# from aero_power_ct_models.aero_models import AeroLookup, powerlaw,

# rotor_radius = 40.0


def PowerModel(model):
    # return powerlaw
    # example = AeroLookup("power_curve.dat").interpolation
    # example2 = powerlaw
    return model


def plantpower(wind_speeds, model):
    plant_power = 0.0
    for velocity in wind_speeds:
        individual_power = PowerModel(model)(velocity)
        plant_power += individual_power
    return plant_power


if __name__ == '__main__':
    from wake_model_mean_new.aero_power_ct_models.aero_models import power_v80
    speeds = [11.0, 9.048160907159671, 8.157923202555526, 7.765198272084803, 7.597142288694455, 7.519434612198159]
    speeds2 = [11.0, 9.006377474720775, 8.237912900926288, 7.853922708596203, 7.624249989366292, 7.469661051011919]
    print plantpower(speeds, power_v80)
    print plantpower(speeds2, power_v80)
