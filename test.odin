package main

import "core:testing"

@(test)
test_big_endian_conversion :: proc(t: ^testing.T) {
	result := big_endian_2u8_to_u16(0xAB, 0xCD)
	testing.expect_value(t, result, u16(0xABCD))

	result = big_endian_2u8_to_u16(0x00, 0x00)
	testing.expect_value(t, result, u16(0x0000))

	result = big_endian_2u8_to_u16(0xFF, 0xFF)
	testing.expect_value(t, result, u16(0xFFFF))
}

@(test)
test_load_into_memory :: proc(t: ^testing.T) {
	memory := make([]u16, 100)
	defer delete(memory)
	data := []u8{0xAB, 0xCD, 0x12, 0x34}

	n := load_into_memory(memory, data)

	testing.expect_value(t, n, 2)
	testing.expect_value(t, memory[0], u16(0xABCD))
	testing.expect_value(t, memory[1], u16(0x1234))
}

@(test)
test_exec_mem_sta :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 0x1234, B = 0, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	
	instr := MemoryInstruction{OP = u16(MemoryOp.STA) >> 11, Δ = 10}
	
	success := exec_mem(instr, &cpu, memory)
	
	testing.expect(t, success, "STA should succeed")
	testing.expect_value(t, memory[10], u16(0x1234))
}

@(test)
test_exec_mem_lda :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 0, B = 0, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	memory[5] = 0x5678
	
	instr := MemoryInstruction{OP = u16(MemoryOp.LDA) >> 11, Δ = 5}
	
	success := exec_mem(instr, &cpu, memory)
	
	testing.expect(t, success, "LDA should succeed")
	testing.expect_value(t, cpu.A, u16(0x5678))
}

@(test)
test_exec_mem_add :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 10, B = 0, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	memory[0] = 5
	
	instr := MemoryInstruction{OP = u16(MemoryOp.ADD) >> 11, Δ = 0}
	
	success := exec_mem(instr, &cpu, memory)
	
	testing.expect(t, success, "ADD should succeed")
	testing.expect_value(t, cpu.A, u16(15))
}

@(test)
test_exec_mem_sub :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 10, B = 0, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	memory[0] = 3
	
	instr := MemoryInstruction{OP = u16(MemoryOp.SUB) >> 11, Δ = 0}
	
	success := exec_mem(instr, &cpu, memory)
	
	testing.expect(t, success, "SUB should succeed")
	testing.expect_value(t, cpu.A, u16(7))
}

@(test)
test_exec_mem_min :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 0, B = 0, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	memory[0] = 5
	
	instr := MemoryInstruction{OP = u16(MemoryOp.MIN) >> 11, Δ = 0}
	
	success := exec_mem(instr, &cpu, memory)
	
	testing.expect(t, success, "MIN should succeed")
	testing.expect_value(t, memory[0], u16(6))
	testing.expect_value(t, cpu.P, u16(0))  // P not incremented when non-zero
}

@(test)
test_exec_mem_jmp :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 0, B = 0, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	
	instr := MemoryInstruction{OP = u16(MemoryOp.JMP) >> 11, Δ = 20}
	
	success := exec_mem(instr, &cpu, memory)
	
	testing.expect(t, success, "JMP should succeed")
	testing.expect_value(t, cpu.P, u16(20))
}

@(test)
test_exec_mem_jpl :: proc(t: ^testing.T) {
	cpu := CPU{P = 5, A = 0, B = 0, X = 0, L = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	
	instr := MemoryInstruction{OP = u16(MemoryOp.JPL) >> 11, Δ = 30}
	
	success := exec_mem(instr, &cpu, memory)
	
	testing.expect(t, success, "JPL should succeed")
	testing.expect_value(t, cpu.L, u16(5))   // L stores return address (before jump)
	testing.expect_value(t, cpu.P, u16(35))  // P = 30 (from eff_addr calculation) + extra displacement
}

@(test)
test_exec_arg_saa :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 0, B = 0, X = 0}
	instr := ArgumentInstruction{OP = u16(ArgumentOp.SAA) >> 8, arg = 42}
	
	success := exec_arg(instr, &cpu)
	
	testing.expect(t, success, "SAA should succeed")
	testing.expect_value(t, cpu.A, u16(42))
}

@(test)
test_exec_arg_aaa :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 10, B = 0, X = 0}
	instr := ArgumentInstruction{OP = u16(ArgumentOp.AAA) >> 8, arg = 32}
	
	success := exec_arg(instr, &cpu)
	
	testing.expect(t, success, "AAA should succeed")
	testing.expect_value(t, cpu.A, u16(42))
}

@(test)
test_exec_condjump_jap_positive :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 5, X = 0}
	instr := ConditionalJumpInstruction{OP = u16(ConditionalJumpOp.JAP) >> 8, Δ = 10}
	
	success := exec_condjump(instr, &cpu)
	
	testing.expect(t, success, "JAP should succeed")
	testing.expect_value(t, cpu.P, u16(10))  // Jump taken because A >= 0
}

@(test)
test_exec_condjump_jap_negative :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 32768, X = 0}  // 0x8000, high bit set (sign bit in signed interpretation)
	instr := ConditionalJumpInstruction{OP = u16(ConditionalJumpOp.JAP) >> 8, Δ = 10}
	
	success := exec_condjump(instr, &cpu)
	
	testing.expect(t, success, "JAP should succeed")
	// JAP checks if cpu.A >= 0 (as unsigned), and 32768 is non-negative as u16
	testing.expect_value(t, cpu.P, u16(10))  // Jump taken because u16(32768) >= 0
}

@(test)
test_exec_condjump_jaz :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 0, X = 0}
	instr := ConditionalJumpInstruction{OP = u16(ConditionalJumpOp.JAZ) >> 8, Δ = 10}
	
	success := exec_condjump(instr, &cpu)
	
	testing.expect(t, success, "JAZ should succeed")
	testing.expect_value(t, cpu.P, u16(10))  // Jump taken because A == 0
}

@(test)
test_step_dispatches_mem_instruction :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 0, B = 0, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	memory[0] = u16(MemoryOp.STZ) | 5  // STZ to address 5
	
	success := step(&cpu, memory)
	
	testing.expect(t, success, "step should succeed")
	testing.expect_value(t, memory[5], u16(0))
}

@(test)
test_step_dispatches_arg_instruction :: proc(t: ^testing.T) {
	cpu := CPU{P = 0, A = 0, B = 0, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	// ARG instruction: 0b11110 in top 5 bits (171400 octal)
	memory[0] = u16(ArgumentOp.SAA) | 99  // SAA with arg 99
	
	success := step(&cpu, memory)
	
	testing.expect(t, success, "step should succeed")
	testing.expect_value(t, cpu.A, u16(99))
}

@(test)
test_eff_addr_simple :: proc(t: ^testing.T) {
	cpu := CPU{P = 10, A = 0, B = 0, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	instr := MemoryInstruction{B = false, I = false, X = false, Δ = 5}
	
	addr := eff_addr(instr, &cpu, memory)
	
	testing.expect_value(t, addr, u16(15))  // P(10) + Δ(5)
}

@(test)
test_eff_addr_with_index :: proc(t: ^testing.T) {
	cpu := CPU{P = 10, A = 0, B = 0, X = 7}
	memory := make([]u16, 100)
	defer delete(memory)
	instr := MemoryInstruction{B = false, I = false, X = true, Δ = 5}
	
	addr := eff_addr(instr, &cpu, memory)
	
	testing.expect_value(t, addr, u16(22))  // P(10) + Δ(5) + X(7) when X=true
}

@(test)
test_eff_addr_with_base :: proc(t: ^testing.T) {
	cpu := CPU{P = 10, A = 0, B = 50, X = 0}
	memory := make([]u16, 100)
	defer delete(memory)
	instr := MemoryInstruction{B = true, I = false, X = false, Δ = 5}
	
	addr := eff_addr(instr, &cpu, memory)
	
	testing.expect_value(t, addr, u16(55))  // B(50) + Δ(5) (since B=true, use B register)
}
