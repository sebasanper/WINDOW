# from util import interpolate
# class LookupTable:
#
#     def __init__(self, file_in):
#
#         with open(file_in, "r") as data:
#             self.x = []
#             self.y = []
#             for line in data:
#                 col = line.split()
#                 self.x.append(float(col[0]))
#                 self.y.append(float(col[1]))
#
#     def interpolation(self, value):
#         ii = 0
#         lower = []
#         upper = []
#         if value <= self.x[0]:
#             print "Found wind speed less than minimum in data"
#             result = self.y[0]
#         else:
#             for x in self.x:
#                 if x <= value:
#                     lower = [x, self.y[ii]]
#                 else:
#                     upper = [x, self.y[ii]]
#                     break
#                 ii += 1
#             result = interpolate(float(lower[0]), float(lower[1]), float(upper[0]), float(upper[1]), value)
#         return result

# outpower = open("windsim_power.dat", "w")
# outct = open("windsim_ct.dat", "w")
#
# with open("windsim_results.dat", "r") as datain:
#     for line in datain:
#         col = line.split()
#         outpower.write("{0} {1}\n".format(col[0], col[1]))
#         outct.write("{0} {1}\n".format(col[0], col[2]))
#
# outpower.close()
# outct.close()

cp = 0.39
a = 0.4
for i in range(40):
    a = cp / (4.0 * (1.0 - a) ** 2.0)
    print 4.0 * a * (1.0 - a)

print str([0,9,8])