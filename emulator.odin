package main

import "core:fmt"

MEMSIZE :: 1 << 16

// Instruction set for the Nord-10/S CPU
Op :: enum u16 {
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
    JMP = 0o124000,
    JPL = 0o134000,
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

// CPU state
CPU :: struct {
    STS, D, P, B, L, A, T, X : u16
}

// TODO: not fully implemented yet
eff_addr :: proc(instr: MemoryInstruction, cpu: ^CPU, mem: []u16) -> u16 {
    addr := cpu.B if instr.B else cpu.P
    addr = u16(i16(addr) + i16(instr.Δ))  // Add displacement TODO: fix this to be correct
    if instr.I { addr = mem[addr] } // Indirect addressing
    if instr.X { addr += cpu.X } // Post-indexing
    return addr
}

step :: proc(cpu: ^CPU, mem: []u16) -> bool {
    iw  := mem[cpu.P]
    // For memory related instructions
    instr := MemoryInstruction(iw)
    el := eff_addr(instr, cpu, mem)
    op := Op(instr.OP << 11)
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
		fmt.printfln("Illegal opcode. %d at P = %d", op, cpu.P)
		return false
    }
    cpu.P += 1
    return true
}

// Hand assembled demo program
demo_program :: proc(mem: []u16) {
    mem[0o0000] = u16(Op.LDA) | 0o000406  // LDA COUNT,B
    mem[0o0001] = u16(Op.MIN) | 0o000406  // MIN COUNT,B
    mem[0o0002] = u16(Op.STA) | 0o000416  // STA VALUE,XI,B
    mem[0o0003] = 0o130001  // JAP 1  (not implemented – triggers error)
}

main :: proc() {
    memory_data : [MEMSIZE]u16
    memory := memory_data[:]  // convert to slice

    cpu := CPU{P = 0, A = 0, T = 0, X = 0, B = 0}

    demo_program(memory)
    fmt.println("Initial CPU state:")
    fmt.printfln("P: %o, A: %o, T: %o, X: %o, B: %o", cpu.P, cpu.A, cpu.T, cpu.X, cpu.B)

    for step(&cpu, memory) {}

    fmt.println("CPU state after execution:")
    fmt.printfln("P: %o, A: %o, T: %o, X: %o, B: %o", cpu.P, cpu.A, cpu.T, cpu.X, cpu.B)
}