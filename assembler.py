#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from collections.abc import Iterable, Iterator
from enum import Enum, auto
from pathlib import Path
from typing import NamedTuple


def parse_command_line_args(argv: list[str]) -> argparse.Namespace:
    """Parse the command line arguments to the script."""
    parser = argparse.ArgumentParser(prog='assembler', description='Assemble NORD-10 assembly code into binary.')
    parser.add_argument('file', type=Path)
    parser.add_argument('-i', '--instructions', type=Path, default=DEFAULT_INSTRUCTIONS_PATH)
    parser.add_argument('-o', '--output', type=Path, default=Path('a.out'))
    args = parser.parse_args(argv)
    assert args.file.exists(), f'Source file {args.file} does not exist.'
    assert args.instructions.exists(), f'Instruction file {args.instructions} does not exit.'
    assert args.instructions.suffix == '.csv', f'Instruction file {args.instructions} is not a csv.'
    return args

DEFAULT_INSTRUCTIONS_PATH = Path(__file__).parent / 'instructions.csv'
LINE_PATTERN = re.compile(
    r'^(?P<label>\w+)?\s+(?P<mnemonic>[A-Z]{3,4})\s+(?P<args>\w+)?(\s*%\s*(?P<comment>.*))?$',
)


class Instruction(NamedTuple):
    i: int
    label: str | None
    mnemonic: str
    args: str
    comment: str | None


def tokenize(f: Iterable[str]) -> Iterator[Instruction]:
    for i, line in enumerate(f, start=1):
        if not line.strip() or line.lstrip().startswith('%'):
            continue  # empty line or comment
        m = LINE_PATTERN.match(line)
        if not m:
            raise ValueError(f'Line {i} not matched "{line}"')
        label = m.group('label')
        mnemonic = m.group('mnemonic')
        args = m.group('args')
        comment = m.group('comment')
        yield Instruction(i=i, label=label, mnemonic=mnemonic, args=args, comment=comment)


class Category(Enum):
    """Categories of instructions."""
    MEM = auto()
    REGBLOCK = auto()
    CONV = auto()
    ARG = auto()
    REG = auto()
    BIT = auto()
    JUMP = auto()
    SHIFT = auto()
    TRANS = auto()


def load_instruction_info(path: Path) -> dict[str, str]:
    """Load instructions from csv file."""
    instructions = {}
    with path.open() as f:
        f.readline()
        for binary, _octal, mnemonic, category, implemented, _desc, _ref in csv.reader(f):
            if not implemented:
                continue
            instructions[mnemonic] = binary, Category[category]
    return instructions


def main(source_path: Path, instructions_path: Path, output_path: Path) -> None:
    instruction_info = load_instruction_info(instructions_path)
    program = bytearray()
    with source_path.open() as f:
        for instruction in tokenize(f):
            binary, category = instruction_info[instruction.mnemonic]
            print(f'Line {instruction} {binary=} {category=}')
            # binary_instruction += TODO
    print(program)
    output_path.write_bytes(program)


if __name__ == '__main__':
    args = parse_command_line_args(sys.argv[1:])
    main(args.file, args.instructions, args.output)
