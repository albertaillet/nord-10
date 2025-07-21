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

// Masks for the three addressing-mode bits
// ┌────────────────────┬───┬───┬───┬─────────────────────┐
// │      OP. CODE      │ X │ I │ B │   Displacement (Δ)  │
// │ 15 │ 14 13 12  │ 11  10  9 │ 8   7 6 │ 5 4 3 │ 2 1 0 │
// └────┴───────────┴───────────┴─────────┴───────┴───────┘
X_MASK : u16 : 0b0000100000000000 // X-bit (post-index)
I_MASK : u16 : 0b0000010000000000 // I-bit (pre-index / indirection)
B_MASK : u16 : 0b0000001000000000 // B-bit (base-relative)

// CPU state
CPU :: struct {
    STS, D, P, B, L, A, T, X : u16
}

// Function to get effective address (not fully implemented yet)
eff_addr :: proc(iw: u16, cpu: ^CPU, mem: []u16) -> u16 {
    base: u16
    if (iw & X_MASK) != 0 {
        base = cpu.X
    } else if (iw & B_MASK) != 0 {
        base = cpu.B
    } else {
        base = cpu.P
    }
    Δ := iw & 0b0000000011111111 // 8-bit displacement
    addr := base + Δ
    if (iw & I_MASK) != 0 {
        addr = mem[addr]
    }
    if (iw & X_MASK) != 0 {
        addr += cpu.X
    }
    return addr
}

step :: proc(cpu: ^CPU, mem: []u16) -> bool {
    iw  := mem[cpu.P]
    cpu.P = (cpu.P + 1)

    op := iw & 0b1111000000000000
    el := eff_addr(iw, cpu, mem)

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
        mem[el] = (mem[el] + 1)
        // skip next instruction if the result is zero
        if mem[el] == 0 { cpu.P = (cpu.P + 1) }
    case LDA_OP:
        cpu.A = mem[el]
    case LDT_OP:
        cpu.T = mem[el]
    case LDX_OP:
        cpu.X = mem[el]
	case:
		fmt.printfln("Illegal opcode: %o at P = %o", iw, cpu.P - 1)
		return false
    }
    return true
}

// Hand assembled demo program
demo_program :: proc(mem: []u16) {
    mem[0o0000] = LDA_OP | 0o000406   // LDA COUNT,B
    mem[0o0001] = MIN_OP | 0o000406   // MIN COUNT,B
    mem[0o0002] = STA_OP | 0o000416   // STA VALUE,XI,B
    mem[0o0003] = 0o060001            // JMP 1  (not implemented – triggers error)
}

main :: proc() {
    memory_data : [MEMSIZE]u16
    memory := memory_data[:]     // convert to slice

    cpu := CPU{P = 0, A = 0, T = 0, X = 0, B = 0}

    demo_program(memory)

    for step(&cpu, memory) {
    }

    fmt.println("CPU state after execution:")
    fmt.printfln("P: %o, A: %o, T: %o, X: %o, B: %o", cpu.P, cpu.A, cpu.T, cpu.X, cpu.B)
}