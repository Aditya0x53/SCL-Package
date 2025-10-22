"""
tests/test_rs.py
"""
import unittest
from finitefield import gf
from polynomial import poly_mul, poly_add, poly_trim
from reedsolomon import rs_encode_msg, rs_decode_msg, simulate_errors

class TestGF(unittest.TestCase):
    def test_mul_div(self):
        for a in [1,2,3,5,10,123]:
            for b in [1,2,4,7,80]:
                prod = gf.mul(a,b)
                if b != 0:
                    self.assertEqual(gf.div(prod, b), a)

class TestPoly(unittest.TestCase):
    def test_mul_add(self):
        a = [1,2]
        b = [3,4]
        r = poly_mul(a,b)
        self.assertIsInstance(r, list)

class TestRS(unittest.TestCase):
    def test_roundtrip_no_errors(self):
        msg = [i for i in range(50)]
        nsym = 10
        cw = rs_encode_msg(msg, nsym)
        out = rs_decode_msg(cw, nsym)
        self.assertEqual(out, msg)

    def test_with_errors(self):
        msg = [i for i in range(30)]
        nsym = 10
        cw = rs_encode_msg(msg, nsym)
        corrupted, positions = simulate_errors(cw, 3)
        decoded = rs_decode_msg(corrupted, nsym)
        self.assertEqual(decoded, msg)

if __name__ == '__main__':
    unittest.main()
