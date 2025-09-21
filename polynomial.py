polynomial.py: Polynomial arithmetic over GF(2^8)

from finitefield import gf

def poly_add(p, q):
    r = [0] * max(len(p), len(q))
    for i in range(len(p)):
        r[i + len(r) - len(p)] = p[i]
    for i in range(len(q)):
        r[i + len(r) - len(q)] ^= q[i]
    return r

def poly_mul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        for j in range(len(q)):
            r[i + j] ^= gf.mul(p[i], q[j])
    return r

def poly_eval(p, x):
    y = p[0]
    for i in range(1, len(p)):
        y = gf.mul(y, x) ^ p[i]
    return y

def poly_div(dividend, divisor):
    output = list(dividend)
    for i in range(len(dividend) - len(divisor) + 1):
        coef = output[i]
        if coef != 0:
            for j in range(1, len(divisor)):
                output[i + j] ^= gf.mul(divisor[j], coef)
    sep = -(len(divisor)-1)
    return output[:sep], output[sep:]

def poly_scale(p, x):
    return [gf.mul(coef, x) for coef in p]