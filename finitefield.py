"""
finitefield.py: GF(2^8) arithmetic for Reed-Solomon coding

Provides:
- GF256 class with exp/log tables
- add/sub/mul/div/inv/pow helpers
- Tables are numpy arrays for speed but public attributes are available
"""
import numpy as np
from typing import List

class GF256:
    # Primitive polynomial for GF(2^8): x^8 + x^4 + x^3 + x^2 + 1 (0x11d)
    prim = 0x11d

    def __init__(self):
        # exp table doubled to simplify index arithmetic
        self.exp: np.ndarray = np.zeros(512, dtype=np.uint8)
        # log table: -inf for 0 is left as 0 but guarded in methods
        self.log: np.ndarray = np.zeros(256, dtype=np.int16)
        self._init_tables()

    def _init_tables(self) -> None:
        x = 1
        for i in range(255):
            self.exp[i] = x
            self.log[x] = i
            x <<= 1
            if x & 0x100:
                x ^= self.prim
        # repeat
        for i in range(255, 512):
            self.exp[i] = self.exp[i - 255]

    # Basic field ops (values are ints 0..255)
    def add(self, x: int, y: int) -> int:
        return x ^ y

    def sub(self, x: int, y: int) -> int:
        return x ^ y

    def mul(self, x: int, y: int) -> int:
        if x == 0 or y == 0:
            return 0
        return int(self.exp[int(self.log[x]) + int(self.log[y])])

    def div(self, x: int, y: int) -> int:
        if y == 0:
            raise ZeroDivisionError("GF division by zero")
        if x == 0:
            return 0
        return int(self.exp[(int(self.log[x]) - int(self.log[y])) % 255])

    def inv(self, x: int) -> int:
        if x == 0:
            raise ZeroDivisionError("GF inverse of zero")
        return int(self.exp[255 - int(self.log[x])])

    def pow(self, x: int, power: int) -> int:
        "Return x**power in GF(2^8). power can be negative."
        if x == 0:
            return 0
        # use logs: x^p = exp[(log[x] * p) mod 255]
        return int(self.exp[(int(self.log[x]) * power) % 255])

# single global instance used by other modules (backwards compatible)
gf = GF256()
