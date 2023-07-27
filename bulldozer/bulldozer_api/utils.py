import itertools


def permutation(p):
    keys, values = zip(*p.items())
    exp = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return exp
