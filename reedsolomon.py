reedsolomon.py: Reed-Solomon encoder/decoder using GF(2^8)

from finitefield import gf
from polynomial import poly_add, poly_mul, poly_eval, poly_div, poly_scale
import numpy as np

def rs_generator_poly(nsym):
    g = [1]
    for i in range(nsym):
        g = poly_mul(g, [1, gf.exp[i]])
    return g

def rs_encode_msg(msg, nsym):
    gen = rs_generator_poly(nsym)
    msg_pad = msg + [0] * nsym
    _, remainder = poly_div(msg_pad, gen)
    codeword = msg + remainder
    return codeword

def rs_calc_syndromes(codeword, nsym):
    synd = []
    for i in range(nsym):
        synd.append(poly_eval(codeword, gf.exp[i]))
    return synd

def rs_correct_errata(codeword, syndromes, err_pos):
    # For brevity, this is a placeholder for real error locator/magnitude algorithms.
    # In practice, use Berlekamp-Massey & Forney's formula.
    # Here, we just flip the bytes at err_pos if syndromes are nonzero.
    for pos in err_pos:
        codeword[pos] ^= syndromes[0]  # naive correction
    return codeword

def rs_find_errors(syndromes, nsym):
    # Naive approach: flip bytes with nonzero syndromes
    return [i for i, s in enumerate(syndromes) if s != 0]

def rs_decode_msg(codeword, nsym):
    syndromes = rs_calc_syndromes(codeword, nsym)
    if max(syndromes) == 0:
        return codeword[:-nsym]  # no error
    err_pos = rs_find_errors(syndromes, nsym)
    corrected = rs_correct_errata(codeword, syndromes, err_pos)
    return corrected[:-nsym]

def simulate_errors(codeword, n_errors):
    import random
    cw = list(codeword)
    positions = random.sample(range(len(cw)), n_errors)
    for pos in positions:
        cw[pos] ^= random.randint(1, 255)
    return cw, positions
