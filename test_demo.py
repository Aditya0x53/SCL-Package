"""
test_demo.py: Demonstration of encoding, error simulation, and decoding using the improved decoder.
"""
from reedsolomon import rs_encode_msg, rs_decode_msg, simulate_errors
from random import randint

msg = [ord(c) for c in "Hello, world! Reed-Solomon"]
nsym = 8

codeword = rs_encode_msg(msg, nsym)
print("Codeword:", codeword)

# introduce up to floor(nsym/2) errors typically
n_errors = 3
corrupted, positions = simulate_errors(codeword, n_errors)
print(f"Corrupted codeword (errors at {positions}):", corrupted)

try:
    recovered = rs_decode_msg(corrupted, nsym)
    print("Recovered message:", bytes(recovered).decode())
except Exception as e:
    print("Decoding failed:", e)
