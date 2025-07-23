package main

import "core:fmt"

// Instruction set for the Nord-10/S CPU
MEMSIZE :: 64 * 1024
STZ_OP : u16 : 0o000000
STA_OP : u16 : 0o004000
STT_OP : u16 : 0o010000
STX_OP : u16 : 0o014000
MIN_OP : u16 : 0o040000
LDA_OP : u16 : 0o044000
LDT_OP : u16 : 0o050000
LDX_OP : u16 : 0o054000
ADD_OP : u16 : 0o060000
SUB_OP : u16 : 0o064000
AND_OP : u16 : 0o070000
ORA_OP : u16 : 0o074000
MPY_OP : u16 : 0o120000

// ┌────────────────────┬───┬───┬───┬─────────────────────┐
// │      OP. CODE      │ X │ I │ B │   Displacement (Δ)  │
// │ 15 │ 14 13 12  │ 11  10  9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
// └────┴───────────┴───────────┴─────────┴───────┴───────┘
MemoryInstruction :: bit_field u16 {
    Δ: u8   | 8,
    B: bool | 1,
    I: bool | 1,
    X: bool | 1,
    OP: u8  | 5,  // NOTE: has to be shifted by 11 to be compared with OP
}

// CPU state
CPU :: struct {
    STS, D, P, B, L, A, T, X : u16
}

// TODO: not fully implemented yet
eff_addr :: proc(instr: MemoryInstruction, cpu: ^CPU, mem: []u16) -> u16 {
    addr := cpu.P if instr.B else cpu.B
    addr = addr + u16(instr.Δ)  // Add displacement
    if instr.I { addr = mem[addr] } // Indirect addressing
    if instr.X { addr += cpu.X } // Post-indexing
    return addr
}

step :: proc(cpu: ^CPU, mem: []u16) -> bool {
    iw  := mem[cpu.P]
    cpu.P += 1

    // For memory related instructions
    instr := MemoryInstruction(iw)
    el := eff_addr(instr, cpu, mem)
    op := u16(instr.OP) << 11
    // TODO: implement more opcodes
    switch op {
    case STZ_OP:
        mem[el] = 0
    case STA_OP:
        mem[el] = cpu.A
    case STT_OP:
        mem[el] = cpu.T
    case STX_OP:
        mem[el] = cpu.X
    case MIN_OP:
        mem[el] += 1
        // skip next instruction if the result is zero
        if mem[el] == 0 { cpu.P += 1 }
    case LDA_OP:
        cpu.A = mem[el]
    case LDT_OP:
        cpu.T = mem[el]
    case LDX_OP:
        cpu.X = mem[el]
    case ADD_OP:
        cpu.A += mem[el]
    case SUB_OP:
        cpu.A -= mem[el]
    case AND_OP:
        cpu.A &= mem[el]
    case ORA_OP:
        cpu.A |= mem[el]
    case MPY_OP:
        cpu.A *= mem[el]
	case:
		fmt.printfln("Illegal opcode: %b at P = %d", op, cpu.P - 1)
		return false
    }
    return true
}

// Hand assembled demo program
demo_program :: proc(mem: []u16) {
    mem[0o0000] = LDA_OP | 0o000406   // LDA COUNT,B
    mem[0o0001] = MIN_OP | 0o000406   // MIN COUNT,B
    mem[0o0002] = STA_OP | 0o000416   // STA VALUE,XI,B
    mem[0o0003] = 0o124001            // JMP 1  (not implemented – triggers error)
}

main :: proc() {
    memory_data : [MEMSIZE]u16
    memory := memory_data[:]     // convert to slice

    cpu := CPU{P = 0, A = 0, T = 0, X = 0, B = 0}

    demo_program(memory)
    fmt.println("Initial CPU state:")
    fmt.printfln("P: %o, A: %o, T: %o, X: %o, B: %o", cpu.P, cpu.A, cpu.T, cpu.X, cpu.B)

    for step(&cpu, memory) {}

    fmt.println("CPU state after execution:")
    fmt.printfln("P: %o, A: %o, T: %o, X: %o, B: %o", cpu.P, cpu.A, cpu.T, cpu.X, cpu.B)
}