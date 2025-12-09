from functools import partial

from flote.backend.python.core.buses import BitBus, BitBusValue
from flote.backend.python.core.component import Component

from abstract import AbsAssignment, alu_out_op, update_reg, update_mem, read_mem, mux_2to1

# Declarations of buses

#* Clock
clk = BitBus()
clk.id = "clk"
clk.value = BitBusValue([False])

#* ALU
alu_a = BitBus()
alu_a.id = "alu_a"
alu_a.value = BitBusValue([False] * 16)
alu_b = BitBus()
alu_b.id = "alu_b"
alu_b.value = BitBusValue([False] * 16)
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

#* Data Memory (32 palavras de 16 bits)
memory_data = [BitBusValue([False] * 16) for _ in range(32)]
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
    alu_a,
    alu_b,
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
] + registers + memory

# Elaboration of the component
#. Clock
clk.influence_list = [bus for bus in registers]

#. ALU
alu_a.assignment = AbsAssignment(lambda: BitBusValue(rf_read_data1.value.raw_value))
alu_a.influence_list = [alu_out]
alu_b.assignment = AbsAssignment(lambda: BitBusValue(rf_read_data2.value.raw_value))
alu_b.influence_list = [alu_out]
alu_out.influence_list = [rf_write_data]
alu_out.assignment = AbsAssignment(partial(alu_out_op, alu_a, alu_b, alu_op))

#. Register Bank
rf_write_enable.influence_list = [bus for bus in registers]

for i, reg in enumerate(registers):
    reg.assignment = AbsAssignment(partial(update_reg, reg, i, rf_write_addr, rf_write_data, clk))

rf_read_addr1.influence_list = [rf_read_data1]
rf_read_data1.assignment = AbsAssignment(
    lambda: BitBusValue(registers[int('0b' + ''.join(['1' if bit else '0' for bit in rf_read_addr1.value.raw_value]), 2)].value.raw_value)
)
rf_read_data1.influence_list = [alu_a]

rf_read_addr2.influence_list = [rf_read_data2]
rf_read_data2.assignment = AbsAssignment(
    lambda: BitBusValue(registers[int('0b' + ''.join(['1' if bit else '0' for bit in rf_read_addr2.value.raw_value]), 2)].value.raw_value)
)
rf_read_data2.influence_list = [alu_b]

rf_write_addr.influence_list = [bus for bus in registers]
rf_write_data.influence_list = [bus for bus in registers]
rf_write_data.assignment = AbsAssignment(lambda: BitBusValue(alu_out.value.raw_value))

mips = Component("mips16x")
for bus in buses:
    assert bus.id is not None, "Bus must have an ID before being added to a component"
    mips.buses[bus.id] = bus
