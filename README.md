# SCL-Package: Reed-Solomon Error Correction Prototype

## Overview

This package provides a lightweight implementation of Reed-Solomon error detection and correction using GF(2^8). It supports encoding and decoding of binary files, error simulation, and includes a CLI and demonstration script.

## Features

- Finite field arithmetic (GF(2^8))
- Polynomial encoding/decoding
- Reed-Solomon codeword construction
- Error simulation for robustness testing
- Simple CLI for file encoding/decoding

## Installation

```bash
pip install numpy
```

## Usage

### Encoding a file

```bash
python cli.py encode input.bin encoded.bin 32
```

### Decoding a file

```bash
python cli.py decode encoded.bin recovered.bin 32
```

### Demo

```bash
python test_demo.py
```

## Module Descriptions

- `finitefield.py`: GF(2^8) arithmetic
- `polynomial.py`: Polynomial operations
- `reedsolomon.py`: Reed-Solomon encoder/decoder
- `cli.py`: Command-line file interface
- `test_demo.py`: Example usage and error simulation

## Notes

- This prototype uses simplified error correction for demonstration.
- For robust applications, extend error locator/magnitude algorithms.

## License

MIT License
