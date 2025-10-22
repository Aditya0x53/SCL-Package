"""
polynomial.py: Polynomial arithmetic over GF(2^8)

Conventions:
- Polynomials are represented as lists of coefficients with highest-degree first.
  Example: [a_n, a_{n-1}, ..., a_0] represents a_n x^n + ... + a_0.
- Functions will generally preserve that ordering.
- Utility poly_trim removes leading zeros.
"""
from typing import List, Tuple
from finitefield import gf

def poly_trim(p: List[int]) -> List[int]:
    "Trim leading zeros; return [0] for the zero polynomial."
    for i, coef in enumerate(p):
        if coef != 0:
            return p[i:]
    return [0]

def poly_add(p: List[int], q: List[int]) -> List[int]:
    r = [0] * max(len(p), len(q))
    for i in range(len(p)):
        r[i + len(r) - len(p)] = p[i]
    for i in range(len(q)):
        r[i + len(r) - len(q)] ^= q[i]
    return poly_trim(r)

def poly_mul(p: List[int], q: List[int]) -> List[int]:
    r = [0] * (len(p) + len(q) - 1)
    for i in range(len(p)):
        for j in range(len(q)):
            r[i + j] ^= gf.mul(p[i], q[j])
    return poly_trim(r)

def poly_scale(p: List[int], x: int) -> List[int]:
    return poly_trim([gf.mul(coef, x) for coef in p])

def poly_eval(p: List[int], x: int) -> int:
    "Evaluate polynomial p at field element x. Horner's method for highest-first coefficients."
    y = 0
    for coef in p:
        y = gf.mul(y, x) ^ coef
    return y

def poly_div(dividend: List[int], divisor: List[int]) -> Tuple[List[int], List[int]]:
    """
    Polynomial long division.
    Returns (quotient, remainder). Both in highest-degree-first order.
    Assumes divisor is non-zero. Works for monic or non-monic divisors.
    """
    # make copies
    out = list(dividend)
    divisor = poly_trim(divisor)
    if divisor == [0]:
        raise ZeroDivisionError("polynomial division by zero")
    normalizer = divisor[0]
    out_len = len(out)
    for i in range(len(dividend) - len(divisor) + 1):
        coef = out[i]
        if coef != 0:
            # factor to eliminate this term
            if normalizer != 1:
                factor = gf.div(coef, normalizer)
            else:
                factor = coef
            out[i] = 0
            for j in range(1, len(divisor)):
                out[i + j] ^= gf.mul(divisor[j], factor)
    sep = -(len(divisor) - 1)
    if sep == 0:
        return poly_trim(out[:]), [0]
    return poly_trim(out[:sep]), poly_trim(out[sep:])
