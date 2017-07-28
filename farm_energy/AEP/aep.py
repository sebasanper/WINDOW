def aep_average(power_farm, availability, electric_efficiency):
    aep = power_farm * availability * electric_efficiency
    return aep


def aep_time(power_farm_time, availability_time, electric_efficiency_time):
    aep = 0.0
    for i in range(len(power_farm_time)):
        aep += power_farm_time[i] * availability_time[i] * electric_efficiency_time[i]
    return aep
