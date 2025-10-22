"""
cli.py: Simple CLI for Reed-Solomon encoding/decoding of files with block handling.

Encoding format:
- Output file layout:
  [4-byte big-endian original length][block1 codeword][block2 codeword]...
This allows exact recovery of original file length after decoding.
"""
import sys
import struct
from reedsolomon import rs_encode_msg, rs_decode_msg, validate_params

BLOCK_HEADER_SIZE = 4  # bytes to store original payload length

def file_to_symbols(filename):
    with open(filename, "rb") as f:
        data = f.read()
    return list(data)

def symbols_to_file(symbols, filename):
    with open(filename, "wb") as f:
        f.write(bytes(symbols))

def encode_file(in_file: str, out_file: str, nsym: int):
    data = file_to_symbols(in_file)
    orig_len = len(data)
    max_msg = 255 - nsym
    if max_msg <= 0:
        raise ValueError("nsym too large; no room for message")
    with open(out_file, "wb") as f:
        # write original length header
        f.write(struct.pack(">I", orig_len))
        # process blocks
        for i in range(0, orig_len, max_msg):
            block = data[i:i+max_msg]
            if len(block) < max_msg:
                # pad with zeros to full block size
                block = block + [0] * (max_msg - len(block))
            codeword = rs_encode_msg(block, nsym)
            f.write(bytes(codeword))
    print(f"Encoded {in_file} -> {out_file} (nsym={nsym})")

def decode_file(in_file: str, out_file: str, nsym: int):
    with open(in_file, "rb") as f:
        raw = f.read()
    if len(raw) < BLOCK_HEADER_SIZE:
        raise ValueError("encoded file too short")
    orig_len = struct.unpack(">I", raw[:4])[0]
    max_msg = 255 - nsym
    codeword_len = max_msg + nsym
    payload = raw[4:]
    if len(payload) % codeword_len != 0:
        raise ValueError("corrupt encoded data: unexpected length")
    out_bytes = []
    for i in range(0, len(payload), codeword_len):
        cw = list(payload[i:i+codeword_len])
        decoded = rs_decode_msg(cw, nsym)
        out_bytes.extend(decoded)
    # trim to original length
    out_bytes = out_bytes[:orig_len]
    symbols_to_file(out_bytes, out_file)
    print(f"Decoded {in_file} -> {out_file} (nsym={nsym})")

def main():
    if len(sys.argv) < 4:
        print("Usage: python cli.py encode|decode input_file output_file [nsym]")
        sys.exit(1)

    action = sys.argv[1]
    in_file = sys.argv[2]
    out_file = sys.argv[3]
    nsym = int(sys.argv[4]) if len(sys.argv) > 4 else 32

    if action == "encode":
        encode_file(in_file, out_file, nsym)
    elif action == "decode":
        decode_file(in_file, out_file, nsym)
    else:
        print("Unknown action. Use encode or decode.")

if __name__ == "__main__":
    main()
