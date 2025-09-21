"""
cli.py: Simple CLI for Reed-Solomon encoding/decoding of files
"""

import sys
from reedsolomon import rs_encode_msg, rs_decode_msg, simulate_errors

def file_to_symbols(filename):
    with open(filename, "rb") as f:
        data = f.read()
    return list(data)

def symbols_to_file(symbols, filename):
    with open(filename, "wb") as f:
        f.write(bytes(symbols))

def main():
    if len(sys.argv) < 4:
        print("Usage: python cli.py encode|decode input_file output_file [nsym]")
        sys.exit(1)

    action = sys.argv[1]
    in_file = sys.argv[2]
    out_file = sys.argv[3]
    nsym = int(sys.argv[4]) if len(sys.argv) > 4 else 32

    symbols = file_to_symbols(in_file)

    if action == "encode":
        codeword = rs_encode_msg(symbols, nsym)
        symbols_to_file(codeword, out_file)
        print(f"Encoded {in_file} with {nsym} parity bytes -> {out_file}")
    elif action == "decode":
        decoded = rs_decode_msg(symbols, nsym)
        symbols_to_file(decoded, out_file)
        print(f"Decoded {in_file} -> {out_file}")
    else:
        print("Unknown action. Use encode or decode.")

if __name__ == "__main__":
    main()