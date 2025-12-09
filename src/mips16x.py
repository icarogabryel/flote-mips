from functools import partial

from flote.backend.python.core.buses import BitBus, BitBusValue
from flote.backend.python.core.component import Component

from abstract import (
    AbsAssignment, alu_out_op, update_reg, update_mem, read_mem, mux_2to1,
    update_pc, extract_opcode, extract_rs, extract_rt, extract_rd, mux_4bit_2to1,
    sign_extend_4to16, mux_alu_src
)

# Declarations of buses

#* Clock
clk = BitBus()
clk.id = "clk"
clk.value = BitBusValue([False])

#* Program Counter (PC)
pc = BitBus()
pc.id = "pc"
pc.value = BitBusValue([False] * 16)

#* Instruction Memory (32 bytes de 8 bits cada)
# Cada instrução de 16 bits ocupa 2 bytes consecutivos
# Formato da instrução: [opcode(4) | rs(4) | rt(4) | rd(4)]
instruction_memory_data = [BitBusValue([False] * 8) for _ in range(32)]  # 32 bytes
instruction_memory = [BitBus() for _ in range(32)]
for i, mem in enumerate(instruction_memory):
    mem.id = f"imem_{i}"
    mem.value = instruction_memory_data[i]

# Instrução atual
instruction = BitBus()
instruction.id = "instruction"
instruction.value = BitBusValue([False] * 16)

# Campos da instrução
opcode = BitBus()
opcode.id = "opcode"
opcode.value = BitBusValue([False] * 4)

rs = BitBus()
rs.id = "rs"
rs.value = BitBusValue([False] * 4)

rt = BitBus()
rt.id = "rt"
rt.value = BitBusValue([False] * 4)

rd = BitBus()
rd.id = "rd"
rd.value = BitBusValue([False] * 4)

# Multiplexador para selecionar entre rt e rd (reg_dst)
reg_dst = BitBus()
reg_dst.id = "reg_dst"
reg_dst.value = BitBusValue([False])

write_reg = BitBus()
write_reg.id = "write_reg"
write_reg.value = BitBusValue([False] * 4)

# Extensor de sinal (rd de 4 bits para 16 bits)
immediate = BitBus()
immediate.id = "immediate"
immediate.value = BitBusValue([False] * 16)

# Sinal de controle ALUSrc
alu_src = BitBus()
alu_src.id = "alu_src"
alu_src.value = BitBusValue([False])

#* ALU
alu_a = BitBus()
alu_a.id = "alu_a"
alu_a.value = BitBusValue([False] * 16)
alu_b = BitBus()
alu_b.id = "alu_b"
alu_b.value = BitBusValue([False] * 16)
alu_b_mux = BitBus()
alu_b_mux.id = "alu_b_mux"
alu_b_mux.value = BitBusValue([False] * 16)
alu_op = BitBus()
alu_op.id = "alu_op"
alu_op.value = BitBusValue([False] * 3)
alu_out = BitBus()
alu_out.id = "alu_out"
alu_out.value = BitBusValue([False] * 16)

#* Register Bank
registers_data = [
    BitBusValue(([False] * 12) + [False, False, True, True]),
    BitBusValue(([False] * 12) + [True, False, False, False]),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
    BitBusValue([False] * 16),
]
registers = [BitBus() for _ in range(16)]
for i, reg in enumerate(registers):
    reg.id = f"reg_{i}"
    reg.value = registers_data[i]

rf_write_enable = BitBus()
rf_write_enable.id = "rf_write_enable"
rf_write_enable.value = BitBusValue([False])

rf_read_addr1 = BitBus()
rf_read_addr1.id = "rf_read_addr1"
rf_read_addr1.value = BitBusValue([False] * 4)
rf_read_data1 = BitBus()
rf_read_data1.id = "rf_read_data1"
rf_read_data1.value = BitBusValue([False] * 16)

rf_read_addr2 = BitBus()
rf_read_addr2.id = "rf_read_addr2"
rf_read_addr2.value = BitBusValue([False] * 4)
rf_read_data2 = BitBus()
rf_read_data2.id = "rf_read_data2"
rf_read_data2.value = BitBusValue([False] * 16)

rf_write_addr = BitBus()
rf_write_addr.id = "rf_write_addr"
rf_write_addr.value = BitBusValue([False] * 4)
rf_write_data = BitBus()
rf_write_data.id = "rf_write_data"
rf_write_data.value = BitBusValue([False] * 16)

#* Data Memory (32 bytes de 8 bits cada)
memory_data = [BitBusValue([False] * 8) for _ in range(32)]  # 32 bytes
memory = [BitBus() for _ in range(32)]
for i, mem in enumerate(memory):
    mem.id = f"mem_{i}"
    mem.value = memory_data[i]

mem_addr = BitBus()
mem_addr.id = "mem_addr"
mem_addr.value = BitBusValue([False] * 16)
mem_write_data = BitBus()
mem_write_data.id = "mem_write_data"
mem_write_data.value = BitBusValue([False] * 16)
mem_read_data = BitBus()
mem_read_data.id = "mem_read_data"
mem_read_data.value = BitBusValue([False] * 16)
mem_write_enable = BitBus()
mem_write_enable.id = "mem_write_enable"
mem_write_enable.value = BitBusValue([False])

#* Multiplexador (seleciona entre alu_out e mem_read_data)
mem_to_reg = BitBus()
mem_to_reg.id = "mem_to_reg"
mem_to_reg.value = BitBusValue([False])
mux_out = BitBus()
mux_out.id = "mux_out"
mux_out.value = BitBusValue([False] * 16)

buses = [
    clk,
    pc,
    instruction,
    opcode,
    rs,
    rt,
    rd,
    reg_dst,
    write_reg,
    immediate,
    alu_src,
    alu_a,
    alu_b,
    alu_b_mux,
    alu_op,
    alu_out,
    rf_write_enable,
    rf_read_addr1,
    rf_read_data1,
    rf_read_addr2,
    rf_read_data2,
    rf_write_addr,
    rf_write_data,
    mem_addr,
    mem_write_data,
    mem_read_data,
    mem_write_enable,
    mem_to_reg,
    mux_out,
] + registers + memory + instruction_memory

# Elaboration of the component
#. Clock
clk.influence_list = [pc] + [bus for bus in registers]

#. Program Counter (PC)
pc.assignment = AbsAssignment(partial(update_pc, pc, clk))
pc.influence_list = [instruction]

#. Instruction Memory (leitura assíncrona)
instruction.assignment = AbsAssignment(partial(read_mem, instruction_memory, pc))
instruction.influence_list = [opcode, rs, rt, rd]

#. Decodificação da Instrução
opcode.assignment = AbsAssignment(partial(extract_opcode, instruction))
opcode.influence_list = []  # Vai para unidade de controle (não implementada ainda)

rs.assignment = AbsAssignment(partial(extract_rs, instruction))
rs.influence_list = [rf_read_addr1]

rt.assignment = AbsAssignment(partial(extract_rt, instruction))
rt.influence_list = [rf_read_addr2, write_reg]

rd.assignment = AbsAssignment(partial(extract_rd, instruction))
rd.influence_list = [write_reg, immediate]

#. Multiplexador reg_dst (seleciona entre rt e rd para o endereço de escrita)
reg_dst.influence_list = [write_reg]
write_reg.assignment = AbsAssignment(partial(mux_4bit_2to1, reg_dst, rt, rd))
write_reg.influence_list = [rf_write_addr]

#. Extensor de sinal (rd de 4 bits para 16 bits para instruções tipo I)
immediate.assignment = AbsAssignment(partial(sign_extend_4to16, rd))
immediate.influence_list = [alu_b_mux]

#. ALU
alu_a.assignment = AbsAssignment(lambda: BitBusValue(rf_read_data1.value.raw_value))
alu_a.influence_list = [alu_out]

# Multiplexador ALUSrc na entrada B da ALU
alu_b.assignment = AbsAssignment(lambda: BitBusValue(rf_read_data2.value.raw_value))
alu_b.influence_list = [alu_b_mux]

alu_src.influence_list = [alu_b_mux]
alu_b_mux.assignment = AbsAssignment(partial(mux_alu_src, alu_src, alu_b, immediate))
alu_b_mux.influence_list = [alu_out]

alu_out.influence_list = [rf_write_data]
alu_out.assignment = AbsAssignment(partial(alu_out_op, alu_a, alu_b_mux, alu_op))

#. Register Bank
rf_write_enable.influence_list = [bus for bus in registers]

for i, reg in enumerate(registers):
    reg.assignment = AbsAssignment(partial(update_reg, reg, i, rf_write_addr, rf_write_data, clk))

# Conectar rs a rf_read_addr1
rf_read_addr1.assignment = AbsAssignment(lambda: BitBusValue(rs.value.raw_value))
rf_read_addr1.influence_list = [rf_read_data1]
rf_read_data1.assignment = AbsAssignment(
    lambda: BitBusValue(registers[int('0b' + ''.join(['1' if bit else '0' for bit in rf_read_addr1.value.raw_value]), 2)].value.raw_value)
)
rf_read_data1.influence_list = [alu_a]

# Conectar rt a rf_read_addr2
rf_read_addr2.assignment = AbsAssignment(lambda: BitBusValue(rt.value.raw_value))
rf_read_addr2.influence_list = [rf_read_data2]
rf_read_data2.assignment = AbsAssignment(
    lambda: BitBusValue(registers[int('0b' + ''.join(['1' if bit else '0' for bit in rf_read_addr2.value.raw_value]), 2)].value.raw_value)
)
rf_read_data2.influence_list = [alu_b, mem_write_data]

# Conectar write_reg a rf_write_addr
rf_write_addr.assignment = AbsAssignment(lambda: BitBusValue(write_reg.value.raw_value))
rf_write_addr.influence_list = [bus for bus in registers]
rf_write_data.influence_list = [bus for bus in registers]
rf_write_data.assignment = AbsAssignment(lambda: BitBusValue(mux_out.value.raw_value))

#. Data Memory
# A saída da ALU entra como endereço da memória
mem_addr.assignment = AbsAssignment(lambda: BitBusValue(alu_out.value.raw_value))
mem_addr.influence_list = [mem_read_data] + memory

# O dado a ser escrito na memória vem do segundo registrador lido
mem_write_data.assignment = AbsAssignment(lambda: BitBusValue(rf_read_data2.value.raw_value))
mem_write_data.influence_list = memory

# Configuração das células de memória
mem_write_enable.influence_list = memory
clk.influence_list = clk.influence_list + memory

for i, mem in enumerate(memory):
    mem.assignment = AbsAssignment(partial(update_mem, mem, i, mem_addr, mem_write_data, mem_write_enable, clk))

# Leitura da memória (assíncrona)
mem_read_data.assignment = AbsAssignment(partial(read_mem, memory, mem_addr))
mem_read_data.influence_list = [mux_out]

#. Multiplexador (mem_to_reg seleciona entre alu_out e mem_read_data)
# Se mem_to_reg = 0: saída da ALU
# Se mem_to_reg = 1: saída da memória
alu_out.influence_list = [mem_addr, mux_out]
mem_to_reg.influence_list = [mux_out]
mux_out.assignment = AbsAssignment(partial(mux_2to1, mem_to_reg, alu_out, mem_read_data))
mux_out.influence_list = [rf_write_data]

mips = Component("mips16x")
for bus in buses:
    assert bus.id is not None, "Bus must have an ID before being added to a component"
    mips.buses[bus.id] = bus
