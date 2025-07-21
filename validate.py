#!/usr/bin/env python3
import csv
from pathlib import Path

instructions_path = Path(__file__).parent / 'instructions.csv'
with instructions_path.open() as f:
    reader = csv.DictReader(f)
    for row in reader:
        assert row['code'], f'Invalid code {row["code"]}'
        if row['binary']:
            assert len(row['binary']) == 16, f'Invalid binary {row["binary"]} for code {row["code"]}'
        if row['octal']:
            assert len(row['octal']) == 6, f'Invalid octal {row["octal"]} for code {row["code"]}'
        if row['octal'] and row['binary']:
            assert int(row['octal'], 8) == int(row['binary'], 2), f'Mismatch between octal {row["octal"]} and binary {row["binary"]} for code {row["code"]}'