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
LINE_PATTERN = re.compile(r'^(?P<label>\w+)?\s+(?P<mnemonic>[A-Z]{3,4})\s+(?P<args>[^\s]+)?(\s*%\s*(?P<comment>.*))?$')


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


class Category(Enum):
    """Categories of instructions."""
    MEM = auto(); REGBLOCK = auto(); CONV = auto(); ARG = auto(); REG = auto(); BIT = auto(); JUMP = auto(); 
    SHIFT = auto(); TRANS = auto(); EXEC = auto(); INTER = auto(); SYS = auto(); WAIT = auto(); IO = auto(); IDENT = auto()


class Instruction(NamedTuple):
    i: int
    label: str | None
    mnemonic: str
    args: str
    comment: str | None
    binary: int
    category: Category


def tokenize(f: Iterable[str], instruction_info: dict[str, tuple[bytes, Category]]) -> Iterator[Instruction]:
    i = 0
    for line in f:
        if not line.strip() or line.lstrip().startswith('%'):
            continue  # empty line or comment
        m = LINE_PATTERN.match(line)
        if not m:
            raise ValueError(f'Line {i} not matched "{line}"')
        i += 1
        label = m.group('label')
        mnemonic = m.group('mnemonic')
        args = m.group('args')
        comment = m.group('comment')
        binary, category = instruction_info[mnemonic]
        yield Instruction(
            i=i, label=label, mnemonic=mnemonic, args=args, comment=comment, binary=binary, category=category
        )


def load_instruction_info(path: Path) -> dict[str, tuple[bytes, Category]]:
    """Load instructions from csv file."""
    instructions = {}
    with path.open() as f:
        f.readline()
        for binary, _octal, mnemonic, category, implemented, _desc, _ref in csv.reader(f):
            if not implemented:
                continue
            instructions[mnemonic] = int(binary, 2), Category[category]
    return instructions


def pass1(instructions: Iterable[Instruction]) -> dict[str, int]:
    labels = {}
    for instruction in instructions:
        if not instruction.label:
            continue
        if instruction.label in labels:
            raise ValueError(f'Repeated label: {instruction.label} at {instruction.i}')
        # NOTE: assumes that each line in the prorgam matches 16 bits, can be more.
        labels[instruction.label] = instruction.i
    return labels


def pass2(instructions: Iterable[Instruction], labels: dict[str, int]) -> bytes:
    program = bytearray()
    for instruction in instructions:
        print(instruction)
    return bytes(program)


def encode(instruction: Instruction, labels: dict[str, int]) -> bytes:
    match instruction.category:
        case Category.MEM:
            return encode_mem(instruction, labels)
        case Category.ARG:
            return encode_arg(instruction, labels)
        case _:
            raise NotImplementedError(f'Category {instruction.category} is not implemented')


def encode_mem(instruction: Instruction, labels: dict[str, int]) -> bytes:
    pass


def encode_arg(instruction: Instruction, labels: dict[str, int]) -> bytes:
    pass


def main(source_path: Path, instructions_path: Path, output_path: Path) -> None:
    instruction_info = load_instruction_info(instructions_path)
    with source_path.open() as f:
        labels = pass1(tokenize(f, instruction_info))
        f.seek(0)
        program = pass2(tokenize(f, instruction_info), labels)
    print(program)
    output_path.write_bytes(program)


if __name__ == '__main__':
    args = parse_command_line_args(sys.argv[1:])
    main(args.file, args.instructions, args.output)
