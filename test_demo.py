"""
test_demo.py: Demonstration of encoding, error simulation, and decoding
"""

from reedsolomon import rs_encode_msg, rs_decode_msg, simulate_errors

msg = [ord(c) for c in "Hello, world! Reed-Solomon"]

nsym = 8

codeword = rs_encode_msg(msg, nsym)
print("Codeword:", codeword)

corrupted, positions = simulate_errors(codeword, n_errors=3)
print(f"Corrupted codeword (errors at {positions}):", corrupted)

recovered = rs_decode_msg(corrupted, nsym)
print("Recovered message:", bytes(recovered).decode())