from memoize import Memoize


def ct_v80(U0):
    if U0 < 4.0:
        return 0.1
    elif U0 <= 25.0:
        return 7.3139922126945e-7 * U0 ** 6.0 - 6.68905596915255e-5 * U0 ** 5.0 + 2.3937885e-3 * U0 ** 4.0 + - 0.0420283143 * U0 ** 3.0 + 0.3716111285 * U0 ** 2.0 - 1.5686969749 * U0 + 3.2991094727
    else:
        return 0.1
ct_v80 = Memoize(ct_v80)


def v80(wind_speed):
    return ct_v80(wind_speed)
v80 = Memoize(v80)

if __name__ == '__main__':
    for i in range(250):
        print i * 0.1, v80(i * 0.1)
