from joblib import Parallel, delayed


def square(kk):
    return kk ** 2.0


def fun(kn):
    return sum(Parallel(n_jobs=-1)(delayed(square)(num) for num in kn))


def root(jj):
    return square(jj) ** 0.5

r1, r2 = Parallel(n_jobs=-1)(delayed(root)(num) for num in range(50))

