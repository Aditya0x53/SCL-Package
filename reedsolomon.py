"""
reedsolomon.py: Reed–Solomon encoder/decoder using GF(2^8)

Provides:
- rs_encode_msg(msg, nsym)
- rs_decode_msg(codeword, nsym) -- decoder using Berlekamp-Massey, Chien search, and Forney
- simulate_errors for testing

Notes:
- This implementation expects polynomials and codewords in highest-degree-first order:
  index 0 is coefficient for x^{n-1} (leftmost byte in lists).
- Encoder is systematic: message bytes first, parity bytes appended.
- Decoder expects codeword length n = k + nsym <= 255
"""
from typing import List, Tuple
from finitefield import gf
from polynomial import poly_mul, poly_div, poly_eval, poly_trim, poly_scale
import random

def rs_generator_poly(nsym: int) -> List[int]:
    "Generate generator polynomial g(x) = prod_{i=0..nsym-1} (x + alpha^{i+1}) in highest-first order."
    g = [1]
    for i in range(nsym):
        g = poly_mul(g, [1, int(gf.exp[i+1])])
    return poly_trim(g)

def rs_encode_msg(msg: List[int], nsym: int) -> List[int]:
    validate_params(len(msg), nsym)
    gen = rs_generator_poly(nsym)
    msg_pad = msg + [0] * nsym
    _, remainder = poly_div(msg_pad, gen)
    codeword = msg + remainder
    return codeword

def rs_calc_syndromes(codeword: List[int], nsym: int) -> List[int]:
    "Return syndromes S1..Snsym (index 0 -> S1). Uses evaluation at alpha^{i+1}."
    synd = []
    for i in range(nsym):
        synd.append(poly_eval(codeword, int(gf.exp[i+1])))
    return synd

# -----------------------------
# Berlekamp-Massey (returns error locator polynomial)
# Work in ascending coefficient order for BM (lowest-degree first)
# -----------------------------
def _to_asc(p: List[int]) -> List[int]:
    "Convert highest-first to ascending (lowest-first)"
    p = poly_trim(p)
    return list(reversed(p))

def _to_desc(p: List[int]) -> List[int]:
    "Convert ascending to highest-first"
    return poly_trim(list(reversed(p)))

def berlekamp_massey(syndromes: List[int]) -> List[int]:
    """
    Berlekamp-Massey algorithm to find error-locator polynomial sigma(x)
    Returns sigma as highest-degree-first list.
    """
    S = list(syndromes)  # S[0] == S1
    N = len(S)
    C = [1]  # connection polynomial (ascending)
    B = [1]
    L = 0
    m = 1
    b = 1

    for n in range(N):
        d = S[n]
        for i in range(1, L+1):
            if i < len(C):
                d ^= gf.mul(C[i], S[n - i])
        if d == 0:
            m += 1
        else:
            T = C.copy()
            coef = gf.div(d, b)
            shift = [0] * m + [gf.mul(coef, bi) for bi in B]
            if len(shift) > len(C):
                C += [0] * (len(shift) - len(C))
            for i in range(len(shift)):
                C[i] ^= shift[i]
            if 2 * L <= n:
                L_new = n + 1 - L
                B = T
                b = d
                L = L_new
                m = 1
            else:
                m += 1
    # C is ascending; convert to highest-first
    return _to_desc(C)

# -----------------------------
# Chien search: find error positions from error-locator polynomial
# -----------------------------
def find_error_positions(error_locator: List[int], nmess: int) -> List[int]:
    """
    error_locator is highest-first polynomial; nmess is codeword length (n)
    Returns list of error indices (0-based from left, matching codeword list index).
    """
    errs = []
    sigma = _to_asc(error_locator)
    for i in range(nmess):
        # Evaluate sigma(alpha^{-i})
        eval_point = int(gf.exp[(255 - i) % 255])  # alpha^{-i}
        val = 0
        power = 1
        for coef in sigma:
            val ^= gf.mul(coef, power)
            power = gf.mul(power, eval_point)
        if val == 0:
            errs.append(i)
    return errs

# -----------------------------
# Forney algorithm: compute error magnitudes
# -----------------------------
def find_error_magnitudes(syndromes: List[int], error_locator: List[int], error_positions: List[int], nmess: int) -> List[int]:
    """
    Compute error magnitudes for positions. Returns list of magnitudes aligned with error_positions.
    Uses Forney's formula with syndromes S1..S2t.
    """
    sigma = _to_asc(error_locator)

    nm = []
    for pos in error_positions:
        Xi = int(gf.exp[(255 - pos) % 255])  # alpha^{-pos}
        # evaluate numerator: sum_{i=0..nsym-1} S[i] * Xi^{i+1}
        num = 0
        Xi_pow = Xi
        for s in syndromes:
            num ^= gf.mul(s, Xi_pow)
            Xi_pow = gf.mul(Xi_pow, Xi)
        # evaluate derivative sigma'(Xi)
        denom = 0
        # derivative: sum_{i=1..t} i * sigma[i] * Xi^{i-1}, sigma ascending
        for i in range(1, len(sigma)):
            if sigma[i] != 0:
                denom ^= gf.mul(gf.mul(i % 255, sigma[i]), gf.pow(Xi, i - 1))
        if denom == 0:
            raise ZeroDivisionError("Forney denominator is zero while computing error magnitude")
        magnitude = gf.div(num, denom)
        nm.append(magnitude)
    return nm

def rs_correct_errata(codeword: List[int], syndromes: List[int], err_pos: List[int]) -> List[int]:
    "Correct codeword at positions err_pos with computed magnitudes (Forney)."
    if not err_pos:
        return codeword
    # build locator from error positions
    sigma = [1]
    for p in err_pos:
        term = [1, int(gf.exp[p])]  # highest-first factor
        sigma = poly_mul(sigma, term)
    sigma = poly_trim(sigma)
    magnitudes = find_error_magnitudes(syndromes, sigma, err_pos, len(codeword))
    cw = list(codeword)
    for pos, mag in zip(err_pos, magnitudes):
        cw[pos] ^= mag
    return cw

def rs_find_errors(syndromes: List[int], nsym: int, n: int) -> List[int]:
    """
    Compute error locator polynomial via Berlekamp-Massey and find error positions via Chien.
    Returns list of error indices (0-based).
    """
    if max(syndromes) == 0:
        return []
    locator = berlekamp_massey(syndromes)
    errs = find_error_positions(locator, n)
    if len(errs) != (len(locator) - 1):
        raise ValueError("Could not locate the correct number of errors")
    return errs

def rs_decode_msg(codeword: List[int], nsym: int) -> List[int]:
    n = len(codeword)
    validate_params(n - nsym, nsym)
    syndromes = rs_calc_syndromes(codeword, nsym)
    if max(syndromes) == 0:
        return codeword[:-nsym]
    err_pos = rs_find_errors(syndromes, nsym, n)
    corrected = rs_correct_errata(codeword, syndromes, err_pos)
    synd2 = rs_calc_syndromes(corrected, nsym)
    if max(synd2) != 0:
        raise ValueError("Could not correct message")
    return corrected[:-nsym]

def simulate_errors(codeword: List[int], n_errors: int) -> Tuple[List[int], List[int]]:
    cw = list(codeword)
    positions = random.sample(range(len(cw)), n_errors)
    for pos in positions:
        cw[pos] ^= random.randint(1, 255)
    return cw, positions

# -----------------------------
# Helpers / validation
# -----------------------------
def validate_params(k_len: int, nsym: int) -> None:
    if not (0 < nsym < 255):
        raise ValueError("nsym must be between 1 and 254")
    if k_len + nsym > 255:
        raise ValueError("message length + nsym must be <= 255")
