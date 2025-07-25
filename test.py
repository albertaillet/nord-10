#!/usr/bin/env python3
import csv

from assembler import DEFAULT_INSTRUCTIONS_PATH, Category, assemble, load_op_info


def test_instructions_csv():
    with DEFAULT_INSTRUCTIONS_PATH.open() as f:
        f.readline()  # skip header
        for binary, octal, mnemonic, category, _impl, _desc, _ref in csv.reader(f):
            assert mnemonic, f'Invalid {mnemonic=}'
            assert Category[category], f'Invalid {category=} for {mnemonic=}'
            if octal:
                assert int(octal, 8) < 2**16, f'Instruction {octal=} exceeds 16 bits.'
                assert len(octal) == 6, f'Invalid {octal=} for {mnemonic=}'
            if binary:
                assert len(binary) == 16, f'Invalid {binary=} for {mnemonic=}'
                assert int(octal, 8) == int(binary, 2), f'Mismatch between {octal=} and {binary=} for {mnemonic=}'

sources = [
# Memory instructions
('	MPY	—',     0b10100_000_00000000),
('	MPY	,X',    0b10100_100_00000000),
('	MPY	I',     0b10100_010_00000000),
('	MPY	,XI',   0b10100_110_00000000),
('	MPY	,B',    0b10100_001_00000000),
('	MPY	,X,B',  0b10100_101_00000000),
('	MPY	I,B',   0b10100_011_00000000),
('	MPY	,XI,B', 0b10100_111_00000000),
('	MPY	127',   0b10100_000_01111111),
# ('	MPY	128',   0b10100_000_01111111),  # raises too big to convert
('	MPY	1',     0b10100_000_00000001),
('	MPY	0',     0b10100_000_00000000),
('	MPY	-1',    0b10100_000_11111111),
('	MPY	-128',  0b10100_000_10000000),
# ('	MPY	-129',  0b10100_000_10000000),  # raises too big to convert
('	MPY	1,XI',  0b10100_110_00000001),
('	MPY	23,XI', 0b10100_110_00010111),
('	MPY	-9,XI', 0b10100_110_11110111),
('	STZ 1',     0b00000_000_00000001),
('	STA 1',     0b00001_000_00000001),
('	STT 1',     0b00010_000_00000001),
('	STX 1',     0b00011_000_00000001),
('	MIN 1',     0b01000_000_00000001),
('	LDA 1',     0b01001_000_00000001),
('	LDT 1',     0b01010_000_00000001),
('	LDX 1',     0b01011_000_00000001),
('	ADD 1',     0b01100_000_00000001),
('	SUB 1',     0b01101_000_00000001),
('	AND 1',     0b01110_000_00000001),
('	ORA 1',     0b01111_000_00000001),
('	MPY 1',     0b10100_000_00000001),
('	JMP 1',     0b10101_000_00000001),
('	JPL 1',     0b10111_000_00000001),
# Argument instructions
('	SAA	-128',  0b11110_001_10000000),
('	SAA	-9',    0b11110_001_11110111),
('	SAA	-1',    0b11110_001_11111111),
('	SAA	0',     0b11110_001_00000000),
('	SAA	1',     0b11110_001_00000001),
('	SAA	23',    0b11110_001_00010111),
('	SAA	127',   0b11110_001_01111111),
('	AAA	1',     0b11110_101_00000001),
('	SAX	1',     0b11110_011_00000001),
('	AAX	1',     0b11110_111_00000001),
('	SAT	1',     0b11110_010_00000001),
('	AAT	1',     0b11110_110_00000001),
('	SAB	1',     0b11110_000_00000001),
('	AAB	1',     0b11110_100_00000001),
# String literals
('	"ab',       0b1100001_01100010),
('	"cern',     0b00110001_10110010_101110010_01101110),
('	"CERN',     0b00100001_10100010_101010010_01001110),
('	"NORD10',   0b01001110_01001111_01010010_01000100_00110001_00110000),
# Numeric literals
('	0',         0b0000_0000_0000_0000),
('	1',         0b0000_0000_0000_0001),
('	65535',     0b1111_1111_1111_1111),
# ('	65536', 0),   # raises too big to convert
# ('	-1',    0),   # not supported
]


if __name__ == '__main__':
    test_instructions_csv()
    op_info = load_op_info(DEFAULT_INSTRUCTIONS_PATH)
    for source, expected in sources:
        out = assemble(source, op_info)
        out_as_int = int.from_bytes(out, 'big')
        l = len(out)*8
        assert out_as_int == expected, f"\n{out_as_int:0{l}b}\n!=\n{expected:0{l}b}\nfor '{source}'"
    print('All tests passed!')

