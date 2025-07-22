# Nord 10 assembler and emulator

## Nord-10/S Documentation

### ND-06.009.01

#### I.1.3.1 Register Block

The CPU has 16 program levels, each level has the following 8 registers:

- **0 STS**  *Status.* This register holds different status indicators.
- **1 D** This register is an extension of the A register in double precision or floating point operations. It may also be connected to the A register during double length shifts.
- **2 P** Program Counter, address of current instruction. This register is controlled automatically in the normal sequencing or branching mode.  But it is also fully program controlled and its contents may be transferred to or from other registers.
- **3 B** Base register or second index register. In connection with indirect addressing, it causes pre-indexing.
- **4 L** *Link register.* The return address after a subroutine jump is contained in this register.
- **5 A** This is the main register for arithmetical and logical operations together with operands in memory. The register is also used for CPU controlled I/O communication.
- **6 T** Temporary register. In floating point instructions it is used to hold the exponent part.
- **7 X** Index register. In connection with indirect addressing, it causes post-indexing.

#### II.3.3.2

Generally, in memory reference instructions, 11 bits are used to specify the address of the desired word(s) in memory. Three address mode bits and an 8-bit signed displacement using 2's complement for negative numbers and sign extension (Excepted from this is the conditional jump, the byte, and the register block instructions).

NORD-10/S uses a relative addressing system, which means that the address is specified relative to the contents of the program counter or relative to the contents of the B and/or X register.

The three addressing mode bits called, `,X`, `I` and `,B` providing eight different addressing modes.

The addressing mode bits have the following meaning:
- The `I` bit specifies indirect addressing
- The `,B` bit specifies address relative to the contents of the B register, pre-indexing. The indexing by B takes place before a possible indirect addressing.
- The `X` bit specifies address relative to the contents of the `X` register post-indexing. The indexing by `X` takes place after a possible indirect addressing.

If all the `,X`, `I` and `,B` bits are zero, the normal relative addressing mode is specified. The effective address is equal to the contents of the program counter plus the displacement (P) + displacement.

The displacement may consist of a number ranging from -128 to +127.
Therefore, this addressing mode gives a dynamic range for directly addressing 128 locations backwards and 127 locations forward.

Note that there is no addition in execution time for relative addressing, pre-indexing, post-indexing or both. Indirect addressing, however, adds one memory cycle to the listed execution times.

#### III.2.1 MEMORY REFERENCE INSTRUCTIONS
```
┌────────────────────┬───┬───┬───┬─────────────────────┐
│      OP. CODE      │ X │ I │ B │   Displacement (Δ)  │
│ 15 │ 14 13 12  │ 11  10  9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
└────┴───────────┴───────────┴─────────┴───────┴───────┘
```

##### Store Instructions

| Mnemonic | Opcode  | Description                 | Address Formula  |
|----------|---------|-----------------------------|------------------|
| —        | 000000  | Address relative to P       | EL = P + Δ       |
| ,X       | 002000  | Address relative to X       | EL = X + Δ       |
| I        | 001000  | Indirect address            | EL = (P + Δ)     |
| ,XI      | 003000  | Post-indexing               | EL = (P + Δ) + X |
| ,B       | 000400  | Address relative to B       | EL = B + Δ       |
| ,X,B     | 002400  | Address relative to B and X | EL = B + Δ + X   |
| I,B      | 001400  | Pre-indexing                | EL = (B + Δ)     |
| ,XI,B    | 003400  | Pre- and Post-indexing      | EL = (B + Δ) + X |

Key:
-	P: Program Counter
-	X: Index register
-	B: Base register
-	I: Indirect addressing
-	Δ: Displacement value

##### Store Instructions

| Mnemonic | Opcode  | Description                       | Operation        |
|----------|---------|-----------------------------------|------------------|
| STZ      | 000000  | Store zero                        | (EL): = 0        |
| STA      | 004000  | Store A                           | (EL): = A        |
| STT      | 010000  | Store T                           | (EL): = T        |
| STX      | 014000  | Store X                           | (EL): = X        |
| MIN      | 040000  | Memory increment and skip if zero | (EL): = (EL) + 1 |

##### Load Instructions

| Mnemonic | Opcode  | Description | Operation |
|----------|---------|-------------|-----------|
| LDA      | 044000  | Load A      | A: = (EL) |
| LDT      | 040000  | Load T      | T: = (EL) |
| LDX      | 054000  | Load X      | X: = (EL) |

##### Arithmetical and Logical Instructions

| Mnemonic | Opcode  | Description                                  | Operation     |
|----------|---------|----------------------------------------------|---------------|
| ADD      | 060000  | Add to A (C, O, and Q may be affected)       | A: = A + (EL) |
| SUB      | 064000  | Subtract from A (C, O, and Q may be affected)| A: = A − (EL) |
| AND      | 070000  | Logical AND to A                             | A: = A ∧ (EL) |
| ORA      | 074000  | Logical inclusive OR to A                    | A: = A ∨ (EL) |
| MPY      | 120000  | Multiply integer (O and Q may be affected)   | A: = A · (EL) |

##### Double Word Instructions

```
    ┌──────────────┬──────────────┐
DA  │  A           │  D           │
    └──────────────┴──────────────┘
    ┌──────────────┬──────────────┐
DW  │  EL          │  EL + 1      │
    └──────────────┴──────────────┘
```

| Mnemonic | Opcode  | Description           | Operation     |
|----------|---------|-----------------------|---------------|
| STD      | 020000  | Store double word     | (DW): = AD    |
| LDD      | 024000  | Load double word      | AD: = (DW)    |

##### Floating Instructions

```
    ┌────────┬────────┬────────┐
TAD │    T   │    A   │    D   │
    └────────┴────────┴────────┘
    ┌────────┬────────┬────────┐
FW  │  EL    │ EL + 1 │ EL + 2 │
    └────────┴────────┴────────┘
```

| Mnemonic | Opcode  | Description                                    | Operation           |
|----------|---------|------------------------------------------------|---------------------|
| STF      | 030000  | Store floating accumulator                     | (FW): = TAD         |
| LDF      | 034000  | Load floating accumulator                      | TAD: = (FW)         |
| FAD      | 100000  | Add to floating accum. (C may also be affected)| TAD: = TAD + (FW)   |
| FSB      | 104000  | Subtract from floating accum. (C may be affected)| TAD: = TAD − (FW) |
| FMU      | 110000  | Multiply floating accum. (C may be affected)   | TAD: = TAD * (FW)   |
| FDV      | 114000  | Divide floating accum. (Z and C may be affected)| TAD: = TAD / (FW)  |

##### Byte Instructions

Addressing: `EL = (T) + (X) / 2`

- Least significant bit of X = 1; Right byte
- Least significant bit of X = 0; Left byte

| Mnemonic | Opcode | Description      |
|----------|--------|------------------|
| SBYT     | 142600 | Store right byte |
| LBYT     | 142200 | Load left byte   |

#### III.2.2 REGISTER BLOCK INSTRUCTIONS

```
┌─────────────────────────────────┬───────────┬───────┐
│  1    1  0  1    0  1  0   1  0 │   Level   │ 0 0 0 │
│                            1  1 │           │ 0 1 0 │
│ 15 │ 14 13 12 │ 11 10  9 │ 8  7 │ 6 │ 5 4 3 │ 2 1 0 │
└────┴──────────┴──────────┴──────┴───┴───────┴───────┘
```

Adressing: `EL = (X)` on current level

| Mnemonic | Opcode | Description                                | Operation  |
|----------|--------|--------------------------------------------|------------|
| LRB      | 152600 | Load register block P on specified level   | = (EL)     |
|          |        | Load register block X on specified level   | = (EL) + 1 |
|          |        | Load register block T on specified level   | = (EL) + 2 |
|          |        | Load register block A on specified level   | = (EL) + 3 |
|          |        | Load register block D on specified level   | = (EL) + 4 |
|          |        | Load register block L on specified level   | = (EL) + 5 |
|          |        | Load register block STS on specified level | = (EL) + 6 |
|          |        | Load register block B on specified level   | = (EL) + 7 |
| SRB      | 152402 | Store register block                       |            |

Specified Level:

| Octal | Binary   | Description |
|-------|----------|-------------|
| 0     | 000000   | Level 0     |
| 01    | 000010   | Level 1     |
| ...   | ...      | ...         |
| 017   | 000170   | Level 15    |

#### III.2.3 FLOATING CONVERSION

```
┌─────────────────────┬──────────┬─────────────────────┐
│  1    1  0  1     0 │ Subinstr │    Scaling factor   │
│ 15 │ 14 13 12  │ 11  10  9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
└────┴───────────┴───────────┴─────────┴───────┴───────┘
```

| Mnemonic | Opcode  | Description                                                    |
|----------|---------|----------------------------------------------------------------|
| NLZ      | 151400  | Convert the number in A to a floating number in FA             |
| DNZ      | 152000  | Convert the floating number in FA to a fixed point number in A |
| NLZ+20   | 151420  | Integer to floating conversion                                 |
| DNZ−20   | 152360  | Floating to integer conversion                                 |

The range of scaling factor is $−128$ to $127$ which gives converting range from $10^{-39}$ to $10^{39}$.

#### III.2.4 ARGUMENT INSTRUCTIONS

```
┌─────────────────────┬──────────┬─────────────────────┐
│  1    1  1  1     0 │ Function │       Argument      │
│ 15 │ 14 13 12  │ 11  10  9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
└────┴───────────┴───────────┴─────────┴───────┴───────┘
```

Function:

| Mnemonic | Opcode | Description       | Operation    |
|----------|--------|-------------------|--------------|
| SAA      | 170400 | Set argument to A | A := ARG     |
| AAA      | 172400 | Add argument to A | A := A + ARG |
| SAX      | 171400 | Set argument to X | X := ARG     |
| AAX      | 173400 | Add argument to X | X := X + ARG |
| SAT      | 171000 | Set argument to T | T := ARG     |
| AAT      | 173000 | Add argument to T | T := T + ARG |
| SAB      | 170000 | Set argument to B | B := ARG     |
| AAB      | 172000 | Add argument to B | B := B + ARG |

Argument is a signed number ranging from $-128$ to $127$.

#### III.2.5 REGISTER OPERATIONS

```
┌─────────────────────┬─────┬───┬───┬───┬───┬───────┬───────┐
│  1    1  0  0     1 │ RAD │ C │ I │CM1│CLD│ Source│  Dest │
│ 15 │ 14 13 12  │ 11    10   9 │ 8   7   6 │ 5 4 3 │ 2 1 0 │
└────┴───────────┴──────────────┴───────────┴───────┴───────┘
```

##### Arithmetic Operations (RAD = 1):

(C, O and Q may be affected by these instructions)

| Mnemonic | Opcode  | Description                         | Operation           |
|----------|---------|-------------------------------------|---------------------|
| RADD     | 146000  | Add source to destination           | (dr) := (dr) + (sr) |
| RSUB     | 146600  | Subtract source from destination    | (dr) := (dr) − (sr) |
| COPY     | 146100  | Register transfer                   | (dr) := (sr)        |
| AD1      | 000400  | Also add one to destination         | (dr) := (dr) + 1    |
| ADC      | 001000  | Also add old carry to destination   | (dr) := (dr) + C    |

##### Logical Operations (RAD = 0)

| Mnemonic | Opcode | Description                        | Operation                  |
|----------|--------|------------------------------------|----------------------------|
| SWAP     | 144000 | Register exchange                  | (sr) := (dr), (dr) := (sr) |
| RAND     | 144400 | Logical AND to destination         | (dr) := (dr) ∧ (sr)        |
| REXO     | 145000 | Logical exclusive OR               | (dr) := (dr) ⊕ (sr)        |
| RORA     | 145400 | Logical inclusive OR               | (dr) := (dr) ∨ (sr)        |
|
| CLD      | 000100 | Clear destination before operation | (dr) := 0                  |
| CM1      | 000200 | Use one’s complement of source     | (sr) := (sr)̅               |

##### Combined instructions

| Mnemonic | Opcode  | Equivalent  | Description            |
|----------|---------|-------------|------------------------|
| EXIT     | 146142  | COPY SL, DP | Return from subroutine |
| RCLR     | 146100  | COPY,       | Register clear         |
| RINC     | 146400  | RADD AD1,   | Register increment     |
| RCDR     | 146200  | RADD CM1,   | Register decrement     |

#### Specify Source Register (sr):

| Mnemonic | Opcode | Description          |
|----------|--------|----------------------|
| SD       | 000010 | D register as source |
| SP       | 000020 | P register as source |
| SB       | 000030 | B register as source |
| SL       | 000040 | L register as source |
| SA       | 000050 | A register as source |
| ST       | 000060 | T register as source |
| SX       | 000070 | X register as source |
| —        | 000000 | Source value = 0     |

#### Specify Destination Register (dr):

| Mnemonic | Opcode | Description               |
|----------|--------|---------------------------|
| DD       | 000001 | D register as destination |
| DP       | 000002 | P register as destination |
| DB       | 000003 | B register as destination |
| DL       | 000004 | L register as destination |
| DA       | 000005 | A register as destination |
| DT       | 000006 | T register as destination |
| DX       | 000007 | X register as destination |

#### Extended Arithmetic Operations

| Mnemonic | Opcode | Description                                                                   | Operation         |
|----------|--------|-------------------------------------------------------------------------------|-------------------|
| RMPY     | 141200 | Multiply source with destination. Result in double accumulator.               | AD := (sr) × (dr) |
| RDIV     | 141600 | Divide double accumulator with source register. Quotient in A, remainder in D | A := AD // (sr)   |

(AD = A<sup>*</sup × (sr) + D)

## References

- CERN documentation https://s3.cern.ch/inspire-prod-files-7/7d44720d4bab506c2032840f87e50689
- Archive.org
  - NorskData search: https://archive.org/search?query=NorskData
  - Nord 10/S manual: https://archive.org/details/NorskData_ND-06.010.01-NORD-10-S-MICROPROGRAM/page/n43/mode/2up
- Forum diskussion about Nord emulator https://forums.bannister.org/ubbthreads.php?ubb=showflat&Number=103978
- Wikipedia https://en.wikipedia.org/wiki/Nord-10
- NDwiki http://www.ndwiki.org/wiki/Main_Page
  - Emulator http://www.ndwiki.org/wiki/Talk:ND100_emulator_project
- datormuseum.se http://www.datormuseum.se/documentation-software/norsk-data-documentation.html
  - ND-06.009.01 | NORD-10/S Functional Description
  - ND-06.010.01 | NORD-10/S MICROPROGRAM
  - ND-06.012.01 | NORD-10/S Input/Output System
  - ND-06.013.01 | NORD-10/S General Description
  - ND-11.009.01 | HAWK Disk System
  - ND-11.010.01 | NORD-10 Hawk Disk Controller
  - ND-11.012.01 | Floppy Disk System
  - ND-30.004.02 | NORD-10/S Hardware Maintenance Manual
  - ND-60.044.01 | SINTRAN II OPERATOR'S GUIDE
  - ND-12.008.01 | NORD 10/HP 7970 Mag Tape interace
- vtda.org https://vtda.org/docs/computing/NorskData/