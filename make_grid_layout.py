with open("layout_grid.dat", "w") as out:
    k = 0
    for i in range(1000):
        for j in range(1000):
            out.write("{} {} {}\n".format(k, i * 1.764, j * 1.764))
            k += 1
