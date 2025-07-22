#!/usr/bin/env python3
import csv
from pathlib import Path

VALID_TYPES = {'MEM','REGBLOCK','CONV','ARG','REG','BIT','JUMP','SHIFT','TRANS','EXEC','INTER','SYS','WAIT','IO','IDENT'}

instructions_path = Path(__file__).parent / 'instructions.csv'
with instructions_path.open() as f:
    reader = csv.DictReader(f)
    for row in reader:
        assert row['code'], f'Invalid code {row["code"]}'
        assert row['type'] in VALID_TYPES, f'Invalid type {row["type"]}'
        if row['binary']:
            assert len(row['binary']) == 16, f'Invalid binary {row["binary"]} for code {row["code"]}'
        if row['octal']:
            assert len(row['octal']) == 6, f'Invalid octal {row["octal"]} for code {row["code"]}'
        if row['octal'] and row['binary']:
            msg = f'Mismatch between octal {row["octal"]} and binary {row["binary"]} for code {row["code"]}'
            assert int(row['octal'], 8) == int(row['binary'], 2), msg
