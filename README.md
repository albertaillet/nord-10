# Nord 10 assembler and emulator

This repository contains documentation and code for an assembler and an emulator of a subset of the instruction set of the 16-bit minicomputer NORD-10 produced by Norsk Data in 1973.

## Nord-10/S Documentation

[ND-06.009.01.md](./ND-06.009.01.md) contains a markdown formatted version of parts of the NORD-10/S Functional Description (See references).

## Usage:

Clone the repo and cd into the folder:
```sh
git clone https://github.com/albertaillet/nord-10
cd nord-10
```
The assembler is written in Python (version 3.13.5 for development, version 3.10 or higher should work).
```sh
./assembler.py --help
```
The emulator is written in the [Odin](https://odin-lang.org/) (version dev-2025-07:090cac62f for development) programming language.
```sh
odin run emulator.odin -file -- <path_to_assembled_program>
```
The tests for the assembler are written in Python and can be run with
```sh
./test.py
```
To assemble a file and then run it:
```sh
./assembler.py examples/arg_instructions.asm -o a.out && odin run emulator.odin -file -- a.out
```
Or compile the emulator first and then run with these commands:
```sh
odin build emulator.odin -file

./assembler.py examples/arg_instructions.asm -o a.out && ./emulator a.out
```


## References

- At CERN https://s3.cern.ch/inspire-prod-files-7/7d44720d4bab506c2032840f87e50689
- Archive.org
  - NorskData search: https://archive.org/search?query=NorskData
  - Nord 10/S manual: https://archive.org/details/NorskData_ND-06.010.01-NORD-10-S-MICROPROGRAM/page/n43/mode/2up
- Forum diskussion about Nord emulator https://forums.bannister.org/ubbthreads.php?ubb=showflat&Number=103978
- Wikipedia https://en.wikipedia.org/wiki/Nord-10
- NDwiki https://www.ndwiki.org/wiki/Main_Page
  - Documentationlist https://www.ndwiki.org/wiki/Documentation_list-Hardware
  - Emulator https://www.ndwiki.org/wiki/Talk:ND100_emulator_project
  - 48-bit floating point http://www.ndwiki.org/wiki/48-bit_floating_point
- vtda.org https://vtda.org/docs/computing/NorskData/
- bitraf.no
  - http://heim.bitraf.no/tingo/files/nd/
  - has a copy of ND-06.014.02 ND-100 Reference Manual January 1982
  - has a copy of ND-06.008 NORD-10/S REFERENCE MAUAL
- bitsavers.org:
  - http://www.bitsavers.org/pdf/norskData/
- datormuseum.se http://www.datormuseum.se/documentation-software/norsk-data-documentation.html

List of scanned documents available at datormuseum.se as of 21/07/2025
|                                                                                                                                          |                                       |
| -----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------|
| [ND-06.009.01](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-06.009.01_NORD-10_S_Functional_Description.pdf)      | NORD-10/S Functional Description      |
| [ND-06.010.01](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-06.010.01-NORD-10-S-MICROPROGRAM.pdf)                | NORD-10/S MICROPROGRAM                |
| [ND-06.012.01](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-06.012.01_NORD-10_S_Input_Output_System.pdf)         | NORD-10/S Input/Output System         |
| [ND-06.013.01](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-06.013.01_NORD-10_S_General_Description.pdf)         | NORD-10/S General Description         |
| [ND-11.009.01](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-11.009.01_HAWK_Disk_System.pdf)                      | HAWK Disk System                      |
| [ND-11.010.01](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-11.010.01_NORD-10_HAWK_DISK_CONTROLLER.pdf)          | NORD-10 Hawk Disk Controller          |
| [ND-11.012.01](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-11.012.01-Floppy-Disk-System.pdf)                    | Floppy Disk System                    |
| [ND-30.004.02](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-30.004.02_NORD-10_S_Hardware_Maintenance_Manual.pdf) | NORD-10/S Hardware Maintenance Manual |
| [ND-60.044.01](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-60.044.01-SINTRAN-II-OPERATORS-GUIDE.pdf)            | SINTRAN II OPERATOR'S GUIDE           |
| [ND-12.008.01](http://storage.datormuseum.se/u/96935524/Datormusuem/ND10/Manuals/ND-12.008.01_NORD_10_HP_7970_Mag_Tape_Interface.pdf)    | NORD 10/HP 7970 Mag Tape interace     |

## Worklog / Notes

### Questions

How it is possible that `LDT` and `MIN` has the same code (`040000`)?
Same question for `SSO` and `SSQ` (`000040`)?
I think it must be a typo and should be `LDT:050000` and `SSO:000050`.

Why does Robert use XOR instead of OR to combine the different 16 bits to the instruction in the Livecode program?

### Notes for later

See USE OF THE PVL REGISTER to get an example of how to use `,X`