#!/usr/bin/env python3
from assembler import DEFAULT_INSTRUCTIONS_PATH, assemble, load_op_info


def as16bit(num: int) -> str:
    return f'{num:016b}'


sources = [
('	MPY	—',     0b10100_000_00000000),
('	MPY	,X',    0b10100_100_00000000),
('	MPY	I',     0b10100_010_00000000),
('	MPY	,XI',   0b10100_110_00000000),
('	MPY	,B',    0b10100_001_00000000),
('	MPY	,X,B',  0b10100_101_00000000),
('	MPY	I,B',   0b10100_011_00000000),
('	MPY	,XI,B', 0b10100_111_00000000),
]


if __name__ == '__main__':
    op_info = load_op_info(DEFAULT_INSTRUCTIONS_PATH)
    for source, expected in sources:
        out = assemble(source, op_info)
        first_2_out_bytes_as_string = f'{out[0]:08b}{out[1]:08b}'
        expected_as_string = as16bit(expected)
        assert first_2_out_bytes_as_string == expected_as_string, f"{first_2_out_bytes_as_string} != {expected_as_string}"
