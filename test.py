#!/usr/bin/env python3
from subprocess import run

from assembler import DEFAULT_INSTRUCTIONS_PATH, assemble, load_op_info


def test_assembler_subprocess(input_asm: str) -> str:
    """Test the assembler CLI with the provided assembly code."""
    process = run(['./assembler.py', '--command', input_asm], capture_output=True, text=True)
    return process.stdout + process.stderr


def as16bit(num: int) -> str:
    return f'{num:016b}'


sources = [
('	MPY	—',     0b1010000000000000),
('	MPY	,X',    0b1010010000000000),
('	MPY	I',     0b1010001000000000),
('	MPY	,XI',   0b1010011000000000),
('	MPY	,B',    0b1010000100000000),
('	MPY	,X,B',  0b1010010100000000),
('	MPY	I,B',   0b1010001100000000),
('	MPY	,XI,B', 0b1010011100000000),
]


if __name__ == '__main__':
    op_info = load_op_info(DEFAULT_INSTRUCTIONS_PATH)
    for source, expected in sources:
        out = assemble(source, op_info)
        print(f'{out[0]:08b}{out[1]:08b}')
        print(as16bit(expected))
