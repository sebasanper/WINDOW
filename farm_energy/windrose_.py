def read_windrose(windrose_file):

    wind_direction = []
    wind_speed = []
    wind_frequency = []

    windrose = open(windrose_file, 'r')

    for line in windrose:
        columns = line.split()
        wind_direction.append(float(columns[0]))
        wind_speed.append(float(columns[1]))
        wind_frequency.append(float(columns[2]))

    return wind_direction, wind_speed, wind_frequency
