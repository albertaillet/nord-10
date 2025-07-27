package main

import "core:fmt"
import "core:os"

MEMSIZE :: 1 << 16

// Instruction set for the Nord-10/S CPU
MemoryOp :: enum u16 {
    STZ = 0o000000,
    STA = 0o004000,
    STT = 0o010000,
    STX = 0o014000,
    MIN = 0o040000,
    LDA = 0o044000,
    LDT = 0o050000,
    LDX = 0o054000,
    ADD = 0o060000,
    SUB = 0o064000,
    AND = 0o070000,
    ORA = 0o074000,
    MPY = 0o120000,
    // Unconditional jumps (MEM format)
    JMP = 0o124000,
    JPL = 0o134000,
}
ArgumentOp :: enum u16 {
    SAA = 0o170400, AAA = 0o172400,
    SAX = 0o171400, AAX = 0o173400,
    SAT = 0o171000, AAT = 0o173000,
    SAB = 0o170000, AAB = 0o172000,
}
ConditionalJumpOp :: enum u16 {
    JAP = 0o130000,
    JAN = 0o130400,
    JAZ = 0o131000,
    JAF = 0o131400,
    JXN = 0o133400,
    JPC = 0o132000,
    JNC = 0o132400,
}


// ┌────────────────────┬───┬───┬───┬─────────────────────┐
// │      OP. CODE      │ X │ I │ B │   Displacement (Δ)  │
// │ 15 │ 14 13 12  │ 11  10  9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
// └────┴───────────┴───────────┴─────────┴───────┴───────┘
MemoryInstruction :: bit_field u16 {
    Δ: i8   | 8,  // Sign extended
    B: bool | 1,
    I: bool | 1,
    X: bool | 1,
    OP: u16 | 5,  // NOTE: has to be shifted by 11 to be compared with Op enum
}

// ┌────────────────────┬──────────┬─────────────────────┐
// │  1    1  1  1    0 │ Function │       Argument      │
// │ 15 │ 14 13 12 │ 11  10  9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
// └────┴──────────┴───────────┴─────────┴───────┴───────┘
ArgumentInstruction :: bit_field u16 {
    arg: i8 | 8,  // Sign extended
    OP: u16 | 8,  // NOTE: has to be shifted by 8 to be compared with Op enum
}

// ┌────────────────────┬───────────┬────────────────────┐
// │  1    0  1  1    0 │ Condition │  Displacement (Δ)  │
// │ 15 │ 14 13 12 │ 11  10  9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
// └────┴──────────┴───────────┴─────────┴───────┴───────┘
ConditionalJumpInstruction :: bit_field u16 {
    Δ  : i8  | 8,  // Sign extended
    OP : u16 | 8,  // NOTE: has to be shifted by 8 to be compared with Op enum
}

// CPU state
CPU :: struct {
    STS, D, P, B, L, A, T, X : u16
}

// TODO: not fully implemented yet
eff_addr :: proc(instr: MemoryInstruction, cpu: ^CPU, mem: []u16) -> u16 {
    addr := cpu.B if instr.B else cpu.P
    addr += u16(instr.Δ)  // Add displacement TODO: fix so negation works
    if instr.I { addr = mem[addr] } // Indirect addressing
    if instr.X { addr += cpu.X } // Post-indexing
    return addr
}

exec_mem :: proc(instr: MemoryInstruction, cpu: ^CPU, mem: []u16) -> bool {
    el := eff_addr(instr, cpu, mem)
    op := MemoryOp(instr.OP << 11)
    switch op {
    case .STZ: mem[el] = 0
    case .STA: mem[el] = cpu.A
    case .STT: mem[el] = cpu.T
    case .STX: mem[el] = cpu.X
    case .MIN: mem[el] += 1; if mem[el] == 0 { cpu.P += 1 }
    case .LDA: cpu.A = mem[el]
    case .LDT: cpu.T = mem[el]
    case .LDX: cpu.X = mem[el]
    case .ADD: cpu.A += mem[el]
    case .SUB: cpu.A -= mem[el]
    case .AND: cpu.A &= mem[el]
    case .ORA: cpu.A |= mem[el]
    case .MPY: cpu.A *= mem[el]
    case .JMP: cpu.P = el
    case .JPL: cpu.L = cpu.P; cpu.P = el
	case:
		fmt.printfln("Illegal MEM opcode. %d at P = %d", op, cpu.P)
		return false
    }
    cpu.P += 1
    return true
}

exec_arg :: proc(instr: ArgumentInstruction, cpu: ^CPU) -> bool {
    op := ArgumentOp(instr.OP << 8)
    arg := u16(instr.arg)  // TODO: fix so negation works
    switch op {
    case .SAA: cpu.A = arg
    case .AAA: cpu.A += arg
    case .SAX: cpu.X = arg
    case .AAX: cpu.X += arg
    case .SAT: cpu.T = arg
    case .AAT: cpu.T += arg
    case .SAB: cpu.B = arg
    case .AAB: cpu.B += arg
    case:
        fmt.printfln("Illegal ARG opcode %o at P=%d", op, cpu.P)
        return false
    }
    return true
}

exec_condjump :: proc(instr: ConditionalJumpInstruction, cpu: ^CPU) -> bool {
    op := ConditionalJumpOp(instr.OP << 8)
    Δ  := u16(instr.Δ) // TODO: fix so negation works
    // TODO: fix so A can be negative (or check for > 127) and that the comparisons are correct
    switch op {
    case .JAP: if cpu.A >= 0 { cpu.P += Δ }
    case .JAN: if cpu.A <  0 { cpu.P += Δ }
    case .JAZ: if cpu.A == 0 { cpu.P += Δ }
    case .JAF: if cpu.A != 0 { cpu.P += Δ }
    case .JXN: if cpu.X <  0 { cpu.P += Δ }
    case .JPC: cpu.X += 1; if cpu.X >= 0 { cpu.P += Δ }
    case .JNC: cpu.X += 1; if cpu.X < 0  { cpu.P += Δ }
    case:
        fmt.printfln("Illegal CONDJUMP opcode %o at P=%d", op, cpu.P)
        return false
    }
    return true
}

step :: proc(cpu: ^CPU, mem: []u16) -> bool {
    instr := mem[cpu.P]
    top5 := instr >> 11
    switch top5 {
    case 0b11110: return exec_arg(ArgumentInstruction(instr), cpu)
    case 0b10110: return exec_condjump(ConditionalJumpInstruction(instr), cpu)
    case:         return exec_mem(MemoryInstruction(instr), cpu, mem)
    }
}

read_input :: proc() -> []u8 {
    if len(os.args) < 2 {
        fmt.println("Usage: emulator.odin -- <filename>");
        os.exit(1);
    }
    data, e := os.read_entire_file_from_filename_or_err(os.args[1], context.allocator);
    if e != os.ERROR_NONE {
        fmt.eprintln("Error reading file: %v", e);
        os.exit(1);
    }
    return data;
}

big_endian_2u8_to_u16 :: proc(b0, b1: u8) -> u16 { 
    return (u16(b0) << 8) | u16(b1);
}

load_into_memory :: proc(mem: []u16, src: []u8) -> int {
    if (len(src) & 1) == 1 { assert(false, "src must be even length"); }
    n := min(len(mem), len(src)/2);
    for i in 0..<n {
        mem[i] = big_endian_2u8_to_u16(src[2*i], src[2*i+1]);
    }
    return n;
}

debug_cpu :: proc(cpu: ^CPU) {
    fmt.printf("P: %o,\tA: %o,\tT: %o,\tX: %o,\tB: %o", cpu.P, cpu.A, cpu.T, cpu.X, cpu.B)
}

debug_memory :: proc(mem: []u16, start: int, end: int) {
    for i in start..<end { 
        fmt.printfln(" %04d: 0o%06o/0b%016b", i, mem[i], mem[i]);
    }
}

main :: proc() {
    memory_data : [MEMSIZE]u16
    memory := memory_data[:]  // convert to slice

    cpu := CPU{P = 0, A = 0, T = 0, X = 0, B = 0}

    program := read_input();
    fmt.println("Got input with", len(program), "bytes");
    n := load_into_memory(memory, program);
    fmt.println("Initial memory contents:");
    debug_memory(memory, 0, n)
    debug_cpu(&cpu)
    fmt.println("   <- Initial CPU state")

    steps := 0
    for step(&cpu, memory) {
        fmt.printfln("\tinstr: 0o%06o/0b%016b", memory[cpu.P], memory[cpu.P])
        cpu.P += 1
        steps += 1
        debug_cpu(&cpu)
        if cpu.P > 15 { break }
        if steps > 20 { break }
    }

    debug_cpu(&cpu)
    fmt.println("   <- End CPU state")
}