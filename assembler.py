#!/bin/python
import argparse
import csv
import sys
from pathlib import Path


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Get arguments from command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=Path)
    parser.add_argument('-hi', '--instructions', type=Path)
    parser.add_argument('-o', '--output', type=Path, default=Path('a.out'))
    args = parser.parse_args(argv)
    assert args.file.exists(), f'Source file {args.file} does not exist.'
    assert args.instructions.exists(), f'Instruction file {args.instructions} does not exit.'
    assert args.instructions.suffix == '.csv', f'Instruction file {args.instructions} is not a csv.'
    return args


def parse_instructions(path: Path) -> dict[str, str]:
    with path.open() as f:
        return {row['code']: row['binary'] for row in csv.DictReader(f)}


def main(source_path: Path, instructions_path: Path, output_path: Path) -> None:
    instructions = parse_instructions(instructions_path)
    with source_path.open() as f:
        for line in f:
            print(line)


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    main(args.file, args.instructions, args.output)
