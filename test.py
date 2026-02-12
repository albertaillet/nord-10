#!/usr/bin/env python3
import csv
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from assembler import DEFAULT_INSTRUCTIONS_PATH, Category, assemble, load_op_info

REPO_ROOT = Path(__file__).parent

def test_instructions_csv():
    with DEFAULT_INSTRUCTIONS_PATH.open() as f:
        f.readline()  # skip header
        for binary, octal, mnemonic, category, _impl, _desc, _ref in csv.reader(f):
            assert mnemonic, f'Invalid {mnemonic=}'
            assert Category[category], f'Invalid {category=} for {mnemonic=}'
            if octal:
                assert int(octal, 8) < 2**16, f'Invalid {octal=} exceeds 16 bits.'
                assert len(octal) == 6, f'Invalid {octal=} for {mnemonic=}'
            if binary:
                assert len(binary) == 16, f'Invalid {binary=} for {mnemonic=}'
                assert int(octal, 8) == int(binary, 2), f'Mismatch between {octal=} and {binary=} for {mnemonic=}'

sources = [
# Formatting
(' MPY 1',     0b10100_000_00000001),
('\tMPY\t1',   0b10100_000_00000001),  # tabs as well
(' MPY 1     ',0b10100_000_00000001),  # extra spaces
('\tMPY\t1\t', 0b10100_000_00000001),  # extra tabs
(' MPY 1 % jk',0b10100_000_00000001),  # comments
(' MPY 1  %j ',0b10100_000_00000001),
('lbl1 MPY 1', 0b10100_000_00000001),  # label
('data "ab',   0b01100001_01100010),   # label and literal
('data 7',     0b00000000_00000111),   # label and literal
# MEMORY REFERENCE INSTRUCTIONS
(' MPY -',     0b10100_000_00000000),
(' MPY ,X',    0b10100_100_00000000),
(' MPY I',     0b10100_010_00000000),
(' MPY ,XI',   0b10100_110_00000000),
(' MPY ,B',    0b10100_001_00000000),
(' MPY ,X,B',  0b10100_101_00000000),
(' MPY I,B',   0b10100_011_00000000),
(' MPY ,XI,B', 0b10100_111_00000000),
(' MPY 127',   0b10100_000_01111111),
(' MPY 128',   OverflowError('int too big to convert')),
(' MPY 1',     0b10100_000_00000001),
(' MPY 0',     0b10100_000_00000000),
(' MPY -1',    0b10100_000_11111111),
(' MPY -128',  0b10100_000_10000000),
(' MPY -129',  OverflowError('int too big to convert')),
(' MPY 1,XI',  0b10100_110_00000001),
(' MPY 23,XI', 0b10100_110_00010111),
(' MPY -9,XI', 0b10100_110_11110111),
## Store Instructions
(' STZ 1',     0b00000_000_00000001),
(' STA 2',     0b00001_000_00000010),
(' STT 3',     0b00010_000_00000011),
(' STX 4',     0b00011_000_00000100),
(' MIN 5',     0b01000_000_00000101),
## Load Instructions
(' LDA 6',     0b01001_000_00000110),
(' LDT 7',     0b01010_000_00000111),
(' LDX 8',     0b01011_000_00001000),
## Arithmetical and Logical Instructions
(' ADD 9',     0b01100_000_00001001),
(' SUB 10',    0b01101_000_00001010),
(' AND 11',    0b01110_000_00001011),
(' ORA 12',    0b01111_000_00001100),
(' MPY 13',    0b10100_000_00001101),
## Double Word Instructions
(' STD 14',    0b00100_000_00001110),
(' LDD 15',    0b00101_000_00001111),
(' STF 16',    0b00110_000_00010000),
(' LDF 17',    0b00111_000_00010001),
## Floating Instructions
(' FAD 18',    0b10000_000_00010010),
(' FSB 19',    0b10001_000_00010011),
(' FMU 20',    0b10010_000_00010100),
(' FDV 21',    0b10011_000_00010101),
# ARGUMENT INSTRUCTIONS
(' SAA -128',  0b11110_001_10000000),
(' SAA -9',    0b11110_001_11110111),
(' SAA -1',    0b11110_001_11111111),
(' SAA 0',     0b11110_001_00000000),
(' SAA 1',     0b11110_001_00000001),
(' SAA 23',    0b11110_001_00010111),
(' SAA 127',   0b11110_001_01111111),
(' AAA 22',    0b11110_101_00010110),
(' SAX 23',    0b11110_011_00010111),
(' AAX 24',    0b11110_111_00011000),
(' SAT 25',    0b11110_010_00011001),
(' AAT 26',    0b11110_110_00011010),
(' SAB 27',    0b11110_000_00011011),
(' AAB 28',    0b11110_100_00011100),
# String Literals
(' "a',        0b1100001_00000000),  # padded to 16 bits
(' "ab',       0b1100001_01100010),
(' "cern',     0b00110001_10110010_101110010_01101110),
(' "CERN',     0b00100001_10100010_101010010_01001110),
(' "NORD10',   0b01001110_01001111_01010010_01000100_00110001_00110000),
(' "NORD-10',  0b01001110_01001111_01010010_01000100_00101101_00110001_00110000_00000000),
# Numeric Literals
(' 0',         0b0000_0000_0000_0000),
(' 1',         0b0000_0000_0000_0001),
(' 65535',     0b1111_1111_1111_1111),
(' 65536',     OverflowError('int too big to convert')),
(' -1',        NotImplementedError('Unknown literal') ),
]

def test_input_output():
    op_info = load_op_info(DEFAULT_INSTRUCTIONS_PATH)
    for source, expected in sources:
        if isinstance(expected, Exception):
            try:
                assemble(source, op_info)
            except Exception as e:
                assert type(e) is type(expected) and e.args == expected.args, f'{e=} != {expected=}'
            else:
                raise AssertionError(f'{source=} did not raise {expected=}.')
        else:
            out = assemble(source, op_info)
            out_as_int = int.from_bytes(out, 'big')
            l = len(out)*8
            assert out_as_int == expected, f"\n{out_as_int:0{l}b}\n!=\n{expected:0{l}b}\nfor '{source}'"


def end_to_end_assembler_to_emulator(source_code: str) -> bytes:
    assembler = subprocess.run([sys.executable, 'assembler.py', '--command', source_code], cwd=REPO_ROOT, capture_output=True, check=True)
    result = subprocess.run(['odin', 'run', 'emulator.odin', '-file'], cwd=REPO_ROOT, input=assembler.stdout, capture_output=True, check=True)
    return result.stdout


def test_end_to_end_assembler_to_emulator():
    source_code = ' SAA 5\n 65535\n'
    result = end_to_end_assembler_to_emulator(source_code).decode()
    assert 'Executed 1 steps' in result
    states = re.findall(r'P:\s*(\d+),\s*A:\s*(\d+),\s*T:\s*(\d+),\s*X:\s*(\d+),\s*B:\s*(\d+)', result)
    assert states, result
    assert states[-1] == ('1', '5', '0', '0', '0')


def test_assembler_accepts_inline_script_argument():
    source_code = ' SAA 5\n 65535\n'
    expected = assemble(source_code, load_op_info(DEFAULT_INSTRUCTIONS_PATH))
    result = subprocess.run([sys.executable, 'assembler.py', '--command', source_code], cwd=REPO_ROOT, capture_output=True, check=True)
    assert result.stdout == expected


class TestNord10(unittest.TestCase):
    def test_instructions_csv(self):
        test_instructions_csv()

    def test_input_output(self):
        test_input_output()

    def test_end_to_end_assembler_to_emulator(self):
        test_end_to_end_assembler_to_emulator()

    def test_assembler_accepts_inline_script_argument(self):
        test_assembler_accepts_inline_script_argument()


if __name__ == '__main__':
    unittest.main()
