def read_layout(layout_file):

    layout_file = open(layout_file, 'r')
    layout = []
    i = 0
    for line in layout_file:
        columns = line.split()
        layout.append([i, float(columns[0]), float(columns[1])])
        i += 1

    return layout

# if __name__ == '__main__':
    # print read_layout("coordinates.dat")
