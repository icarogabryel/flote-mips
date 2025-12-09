from flote.testbench import TestBench
from flote.backend.python.core.buses import BitBusValue

import mips16x

# Programa de teste:
# Instrução 0 (endereço 0-1): ADDI $1, $0, 5   -> reg[1] = reg[0] + 5 = 5
# Instrução 1 (endereço 2-3): ADDI $2, $0, 3   -> reg[2] = reg[0] + 3 = 3
# Instrução 2 (endereço 4-5): ADD  $3, $1, $2  -> reg[3] = reg[1] + reg[2] = 8
# Instrução 3 (endereço 6-7): SUB  $4, $3, $2  -> reg[4] = reg[3] - reg[2] = 5
# Instrução 4 (endereço 8-9): SLT  $5, $2, $1  -> reg[5] = (reg[2] < reg[1]) = 1

# ADDI $1, $0, 5 -> opcode=0101, rs=0000, rt=0001, imm=0101
mips16x.instruction_memory[0].value = BitBusValue([False, True, False, True, False, False, False, False])  # Byte 0: 0101 0000
mips16x.instruction_memory[1].value = BitBusValue([False, False, False, True, False, True, False, True])  # Byte 1: 0001 0101

# ADDI $2, $0, 3 -> opcode=0101, rs=0000, rt=0010, imm=0011
mips16x.instruction_memory[2].value = BitBusValue([False, True, False, True, False, False, False, False])  # Byte 2: 0101 0000
mips16x.instruction_memory[3].value = BitBusValue([False, False, True, False, False, False, True, True])  # Byte 3: 0010 0011

# ADD $3, $1, $2 -> opcode=0000, rs=0001, rt=0010, rd=0011
mips16x.instruction_memory[4].value = BitBusValue([False, False, False, False, False, False, False, True])  # Byte 4: 0000 0001
mips16x.instruction_memory[5].value = BitBusValue([False, False, True, False, False, False, True, True])  # Byte 5: 0010 0011

# SUB $4, $3, $2 -> opcode=0001, rs=0011, rt=0010, rd=0100
mips16x.instruction_memory[6].value = BitBusValue([False, False, False, True, False, False, True, True])  # Byte 6: 0001 0011
mips16x.instruction_memory[7].value = BitBusValue([False, False, True, False, False, True, False, False])  # Byte 7: 0010 0100

# SLT $5, $2, $1 -> opcode=0100, rs=0010, rt=0001, rd=0101
mips16x.instruction_memory[8].value = BitBusValue([False, True, False, False, False, False, True, False])  # Byte 8: 0100 0010
mips16x.instruction_memory[9].value = BitBusValue([False, False, False, True, False, True, False, True])  # Byte 9: 0001 0101

print("=== MIPS 16-bit Monociclo - Testbench Completo ===\n")
print("Programa:")
print("0: ADDI $1, $0, 5   -> reg[1] = 5")
print("2: ADDI $2, $0, 3   -> reg[2] = 3")
print("4: ADD  $3, $1, $2  -> reg[3] = 8")
print("6: SUB  $4, $3, $2  -> reg[4] = 5")
print("8: SLT  $5, $2, $1  -> reg[5] = 1 (3 < 5)")
print("\n" + "="*50 + "\n")

tb = TestBench(mips16x.mips)
tb.set_time_unit('ns')

# Executar 10 ciclos de clock (5 instruções)
for i in range(10):
    # Fase baixa do clock
    tb.update({'clk': '0'})
    tb.wait(5)

    # Fase alta do clock (atualiza PC e registradores)
    tb.update({'clk': '1'})
    tb.wait(5)

    print(f"Ciclo {i+1} completo")

tb.save_vcd('mips16x_test.vcd')
print("\n" + "="*50)
print("Simulação concluída! Arquivo VCD gerado: mips16x_test.vcd")

print("\nValores reais dos registradores após simulação:")
for i in range(6):
    reg_value = int('0b' + ''.join(['1' if bit else '0' for bit in mips16x.registers[i].value.raw_value]), 2)
    print(f"reg[{i}] = {reg_value}")

print("\nResultados esperados nos registradores:")
print("reg[1] = 5")
print("reg[2] = 3")
print("reg[3] = 8")
print("reg[4] = 5")
print("reg[5] = 1")
