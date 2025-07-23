#!/usr/bin/env python3
import csv
from pathlib import Path

from assembler import Category

instructions_path = Path(__file__).parent / 'instructions.csv'
with instructions_path.open() as f:
    f.readline()  # header
    for binary, octal, mnemonic, category, _impl, _desc, _ref in csv.reader(f):
        assert mnemonic, f'Invalid {mnemonic=}'
        assert Category[category], f'Invalid type {category=} for {mnemonic=}'
        if octal:
            assert int(octal, 8) < 2**16, f'Instruction {octal=} exceeds 16 bits.'
            assert len(octal) == 6, f'Invalid {octal=} for {mnemonic=}'
        if binary:
            assert len(binary) == 16, f'Invalid {binary=} for {mnemonic=}'
            assert int(octal, 8) == int(binary, 2), f'Mismatch between {octal=} and {binary=} for {mnemonic=}'
