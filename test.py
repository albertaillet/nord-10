#!/usr/bin/env python3
from assembler import DEFAULT_INSTRUCTIONS_PATH, assemble, load_op_info

sources = [
('	MPY	—',     0b10100_000_00000000),
('	MPY	,X',    0b10100_100_00000000),
('	MPY	I',     0b10100_010_00000000),
('	MPY	,XI',   0b10100_110_00000000),
('	MPY	,B',    0b10100_001_00000000),
('	MPY	,X,B',  0b10100_101_00000000),
('	MPY	I,B',   0b10100_011_00000000),
('	MPY	,XI,B', 0b10100_111_00000000),
('	MPY	127',   0b10100_000_01111111),
('	MPY	1',     0b10100_000_00000001),
('	MPY	0',     0b10100_000_00000000),
('	MPY	-1',    0b10100_000_11111111),
('	MPY	-128',  0b10100_000_10000000),
('	MPY	1,XI',  0b10100_110_00000001),
('	MPY	23,XI', 0b10100_110_00010111),
('	MPY	-9,XI', 0b10100_110_11110111),
]


if __name__ == '__main__':
    op_info = load_op_info(DEFAULT_INSTRUCTIONS_PATH)
    for source, expected in sources:
        out = assemble(source, op_info)
        out_as_int = int.from_bytes(out, 'big')
        assert out_as_int == expected, f'{out_as_int:0{len(out)*8}b} != {expected:016b}'
