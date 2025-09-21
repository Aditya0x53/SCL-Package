"""
finitefield.py: GF(2^8) arithmetic for Reed-Solomon coding
"""

import numpy as np

class GF256:
    # Primitive polynomial for GF(2^8): x^8 + x^4 + x^3 + x^2 + 1 (0x11d)
    prim = 0x11d

    def __init__(self):
        self.exp = np.zeros(512, dtype=np.uint8)
        self.log = np.zeros(256, dtype=np.int16)
        self._init_tables()

    def _init_tables(self):
        x = 1
        for i in range(255):
            self.exp[i] = x
            self.log[x] = i
            x <<= 1
            if x & 0x100:
                x ^= self.prim
        for i in range(255, 512):
            self.exp[i] = self.exp[i - 255]

    def add(self, x, y):
        return x ^ y

    def sub(self, x, y):
        return x ^ y

    def mul(self, x, y):
        if x == 0 or y == 0:
            return 0
        return self.exp[self.log[x] + self.log[y]]

    def div(self, x, y):
        if y == 0:
            raise ZeroDivisionError()
        if x == 0:
            return 0
        return self.exp[(self.log[x] - self.log[y]) % 255]

    def inv(self, x):
        if x == 0:
            raise ZeroDivisionError()
        return self.exp[255 - self.log[x]]

gf = GF256()