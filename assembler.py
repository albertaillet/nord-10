#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from collections.abc import Iterable, Iterator
from enum import Enum, auto
from pathlib import Path
from typing import NamedTuple

DEFAULT_INSTRUCTIONS_PATH = Path(__file__).parent / 'instructions.csv'
LINE_PATTERN = re.compile(r'^(?P<label>\w+)?\s*(?P<mnemonic>[A-Z]{3,4})?\s*(?P<args>[^\s^%]+)?\s*(?:%\s*(?P<comment>.*))?$')


def parse_command_line_args(argv: list[str]) -> argparse.Namespace:
    """Parse the command line arguments to the script."""
    parser = argparse.ArgumentParser(prog='assembler', description='Assemble NORD-10 assembly code into binary.')
    parser.add_argument('file', type=Path, nargs='?', default=None, help='Assembly source file or "-" to read from stdin.')
    parser.add_argument('-i', '--instructions', type=Path, default=DEFAULT_INSTRUCTIONS_PATH)
    parser.add_argument('-o', '--output', type=Path, default=None)
    parser.add_argument('-c', '--command', type=str, default=None, help='Program passed in as a string (terminates option list).')
    args = parser.parse_args(argv)
    assert args.file is None or args.file.exists(), f'Source file {args.file} does not exist.'
    assert not (args.command and args.file), 'Use either a file or a command string.'
    assert args.instructions.exists(), f'Instruction file {args.instructions} does not exist.'
    assert args.instructions.suffix == '.csv', f'Instruction file {args.instructions} is not a csv.'
    return args


class Category(Enum):
    """Categories of instructions."""
    MEM = auto(); REGBLOCK = auto(); CONV = auto(); ARG = auto(); REG = auto(); BIT = auto(); CONDJUMP = auto(); SKIP = auto(); SHIFT = auto()
    TRANS = auto(); EXEC = auto(); INTER = auto(); SYS = auto(); WAIT = auto(); IO = auto(); IDENT = auto(); LITERAL = auto()


class Instruction(NamedTuple):
    line_num: int
    address: int
    label: str | None
    mnemonic: str | None
    args: str | None
    comment: str | None
    binary: int | None
    category: Category


def tokenize(f: Iterable[str], instruction_info: dict[str, tuple[int, Category]]) -> Iterator[Instruction]:
    address = 0
    for line_num, line in enumerate(f, start=1):
        if not line.strip() or line.lstrip().startswith('%'):
            continue  # empty line or comment
        m = LINE_PATTERN.match(line)
        if not m:
            raise ValueError(f'Line {line_num} not matched "{line}"')
        label = m.group('label')
        mnemonic = m.group('mnemonic')
        args = m.group('args')
        comment = m.group('comment')
        binary, category = instruction_info.get(mnemonic, (None, Category.LITERAL))
        instr = Instruction(
            line_num=line_num, address=address, label=label, mnemonic=mnemonic, args=args, comment=comment, binary=binary, category=category
        )
        yield instr
        address += instruction_length(instr)


def load_op_info(path: Path) -> dict[str, tuple[int, Category]]:
    op_info = {}
    with path.open() as f:
        f.readline()
        for binary, _octal, mnemonic, category, implemented, _desc, _ref in csv.reader(f):
            if not implemented:
                continue
            op_info[mnemonic] = int(binary, 2), Category[category]
    return op_info


def pass1(instructions: Iterable[Instruction]) -> dict[str, int]:
    """First pass to create {labels -> addresses} symbol_table."""
    symbol_table = {}
    for instr in instructions:
        if instr.label:
            if instr.label in symbol_table:
                raise ValueError(f'Repeated label: {instr.label} at {instr.i}')
            symbol_table[instr.label] = instr.address
    return symbol_table


def pass2(instructions: Iterable[Instruction], symbol_table: dict[str, int]) -> bytes:
    """Second pass to construct program."""
    program = bytearray()
    for instr in instructions:
        program += encode(instr, symbol_table)
    return bytes(program)


def encode(instr: Instruction, symbol_table: dict[str, int]) -> bytes:
    match instr.category:
        case Category.MEM: return encode_mem(instr, symbol_table)
        case Category.ARG: return encode_arg(instr)
        case Category.LITERAL:  # literals (not an instruction, can be multiple 16 bit values)
            if instr.args.isdigit(): return int(instr.args).to_bytes(2, 'big')  # numeric literal # NOTE: supports up to 2^16
            if instr.args.startswith('"'): return instr.args[1:].encode('ascii')  # string literal TODO: pad this to 16-bit (now it could be 8-bit)
            raise NotImplementedError('Unknown literal')
        case _:
            raise NotImplementedError(f'Category {instr.category} is not implemented')


def instruction_length(instr: Instruction) -> int:
    match instr.category:
        case Category.MEM | Category.ARG: return 1
        case Category.LITERAL:
            if instr.args.isdigit(): return 1
            if instr.args.startswith('"'): return len(instr.args[1:].encode('ascii')) // 2
            raise NotImplementedError('Unknown literal')
        case _:
            raise NotImplementedError(f'Category {instr.category} is not implemented')


def encode_signed_int8(value: int) -> int:
    """Encode a signed int to bytes and back: x -> x if x > 0 else x -> 256 - x (-128 <= x <= 127)."""
    return int.from_bytes(value.to_bytes(1, 'big', signed=True))


# ┌───────────────────┬───┬───┬───┬─────────────────────┐
# │      OP. CODE     │ X │ I │ B │   Displacement (Δ)  │
# │ 15 │ 14 13 12 │ 11 10   9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
# └────┴──────────┴───────────┴─────────┴───────┴───────┘
MEM_PATTERN = re.compile(r'^(?:(?P<delta>-?\d*)|(?P<label>\w+))(?P<X>,X)?(?P<I> ?I)?(?P<B>,B)?$')
def encode_mem(instr: Instruction, symbol_table: dict[str, int]) -> bytes:
    m = MEM_PATTERN.match(instr.args)
    Δ, x, i, b = 0, bool(m.group('X')), bool(m.group('I')), bool(m.group('B'))
    if (delta := m.group('delta')): Δ = encode_signed_int8(0 if delta == '-' else int(delta))
    if (label := m.group('label')): Δ = encode_signed_int8(instr.address - symbol_table[label])
    return (instr.binary | (x << 10) | (i << 9) | (b << 8) | Δ).to_bytes(2, 'big')


# ┌────────────────────┬──────────┬─────────────────────┐
# │  1    1  1  1    0 │ Function │       Argument      │
# │ 15 │ 14 13 12 │ 11  10  9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
# └────┴──────────┴───────────┴─────────┴───────┴───────┘
def encode_arg(instr: Instruction) -> bytes:
    argument = encode_signed_int8(int(instr.args or 0))
    return (instr.binary | argument).to_bytes(2, 'big')


def print_program(program: bytes) -> None:
    for i in range(0, len(program), 2):
        print(f'{program[i]:08b}{program[i + 1]:08b}')


def assemble(source_code: str, op_info: dict[str, tuple[int, Category]]) -> bytes:
    source_lines = source_code.splitlines()
    tokens = list(tokenize(source_lines, op_info))
    symbol_table = pass1(tokens)
    return pass2(tokens, symbol_table)


def read_input_file(source_path: Path | None) -> str:
    if source_path is None:
        if sys.stdin.isatty():  # Stdin is from a terminal (nothing piped)
            raise ValueError('No input file provided and no input received from stdin.')
        return sys.stdin.read()
    return source_path.read_text()


if __name__ == '__main__':
    args = parse_command_line_args(sys.argv[1:])
    source_code = args.command or read_input_file(args.file)
    op_info = load_op_info(args.instructions)
    program = assemble(source_code, op_info)
    print_program(program)
    if args.output:
        args.output.write_bytes(program)
