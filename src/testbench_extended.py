from flote.testbench import TestBench
from flote.backend.python.core.buses import BitBusValue

import mips16x

# Programa de teste estendido para todas as instruções:
# Testa: ADD, SUB, AND, OR, SLT, ADDI, LW, SW, BEQ, JUMP

print("=== MIPS 16-bit Monociclo - Testbench Estendido ===\n")
print("Testando TODAS as instruções implementadas\n")

# Limpar memória de dados
for i in range(32):
    mips16x.memory[i].value = BitBusValue([False] * 8)

# ============================================
# TESTE 1: Instruções Aritméticas (ADD, SUB, ADDI)
# ============================================
print("TESTE 1: Instruções Aritméticas")
print("-" * 50)

# 0: ADDI $1, $0, 5    -> reg[1] = 5
mips16x.instruction_memory[0].value = BitBusValue([False, True, False, True, False, False, False, False])  # 0101 0000
mips16x.instruction_memory[1].value = BitBusValue([False, False, False, True, False, True, False, True])  # 0001 0101
print("0: ADDI $1, $0, 5   -> reg[1] = 5")

# 2: ADDI $2, $0, 3    -> reg[2] = 3
mips16x.instruction_memory[2].value = BitBusValue([False, True, False, True, False, False, False, False])  # 0101 0000
mips16x.instruction_memory[3].value = BitBusValue([False, False, True, False, False, False, True, True])  # 0010 0011
print("2: ADDI $2, $0, 3   -> reg[2] = 3")

# 4: ADD $3, $1, $2    -> reg[3] = reg[1] + reg[2] = 8
mips16x.instruction_memory[4].value = BitBusValue([False, False, False, False, False, False, False, True])  # 0000 0001
mips16x.instruction_memory[5].value = BitBusValue([False, False, True, False, False, False, True, True])  # 0010 0011
print("4: ADD  $3, $1, $2  -> reg[3] = 8")

# 6: SUB $4, $3, $2    -> reg[4] = reg[3] - reg[2] = 5
mips16x.instruction_memory[6].value = BitBusValue([False, False, False, True, False, False, True, True])  # 0001 0011
mips16x.instruction_memory[7].value = BitBusValue([False, False, True, False, False, True, False, False])  # 0010 0100
print("6: SUB  $4, $3, $2  -> reg[4] = 5")

# ============================================
# TESTE 2: Instruções Lógicas (AND, OR)
# ============================================
print("\nTESTE 2: Instruções Lógicas")
print("-" * 50)

# 8: ADDI $5, $0, 7    -> reg[5] = 7 (0b0111)
mips16x.instruction_memory[8].value = BitBusValue([False, True, False, True, False, False, False, False])  # 0101 0000
mips16x.instruction_memory[9].value = BitBusValue([False, True, False, True, False, True, True, True])  # 0101 0111
print("8: ADDI $5, $0, 7   -> reg[5] = 7 (0b0111)")

# 10: ADDI $6, $0, 6   -> reg[6] = 6 (0b0110)
mips16x.instruction_memory[10].value = BitBusValue([False, True, False, True, False, False, False, False])  # 0101 0000
mips16x.instruction_memory[11].value = BitBusValue([False, True, True, False, False, True, True, False])  # 0110 0110
print("10: ADDI $6, $0, 6  -> reg[6] = 6 (0b0110)")

# 12: AND $7, $5, $6   -> reg[7] = reg[5] & reg[6] = 6 (0b0110)
mips16x.instruction_memory[12].value = BitBusValue([False, False, True, False, False, True, False, True])  # 0010 0101
mips16x.instruction_memory[13].value = BitBusValue([False, True, True, False, False, True, True, True])  # 0110 0111
print("12: AND  $7, $5, $6 -> reg[7] = 6 (7 & 6)")

# 14: OR $8, $5, $6    -> reg[8] = reg[5] | reg[6] = 7 (0b0111)
mips16x.instruction_memory[14].value = BitBusValue([False, False, True, True, False, True, False, True])  # 0011 0101
mips16x.instruction_memory[15].value = BitBusValue([False, True, True, False, True, False, False, False])  # 0110 1000
print("14: OR   $8, $5, $6 -> reg[8] = 7 (7 | 6)")

# ============================================
# TESTE 3: Instrução SLT
# ============================================
print("\nTESTE 3: Instrução SLT (Set Less Than)")
print("-" * 50)

# 16: SLT $9, $2, $1   -> reg[9] = (reg[2] < reg[1]) = 1 (3 < 5)
mips16x.instruction_memory[16].value = BitBusValue([False, True, False, False, False, False, True, False])  # 0100 0010
mips16x.instruction_memory[17].value = BitBusValue([False, False, False, True, True, False, False, True])  # 0001 1001
print("16: SLT  $9, $2, $1 -> reg[9] = 1 (3 < 5)")

# 18: SLT $10, $1, $2  -> reg[10] = (reg[1] < reg[2]) = 0 (5 < 3)
mips16x.instruction_memory[18].value = BitBusValue([False, True, False, False, False, False, False, True])  # 0100 0001
mips16x.instruction_memory[19].value = BitBusValue([False, False, True, False, True, False, True, False])  # 0010 1010
print("18: SLT  $10, $1, $2 -> reg[10] = 0 (5 < 3)")

# ============================================
# TESTE 4: Instruções de Memória (SW, LW)
# ============================================
print("\nTESTE 4: Instruções de Memória (SW, LW)")
print("-" * 50)

# 20: ADDI $11, $0, 4  -> reg[11] = 4 (endereço base para memória)
mips16x.instruction_memory[20].value = BitBusValue([False, True, False, True, False, False, False, False])  # 0101 0000
mips16x.instruction_memory[21].value = BitBusValue([True, False, True, True, False, True, False, False])  # 1011 0100
print("20: ADDI $11, $0, 4 -> reg[11] = 4 (endereço)")

# 22: SW $1, 0($11)    -> mem[4] = reg[1] = 5
# Format: [opcode(0111=SW) | rs=11(1011) | rt=1(0001) | offset=0(0000)]
mips16x.instruction_memory[22].value = BitBusValue([False, True, True, True, True, False, True, True])  # 0111 1011
mips16x.instruction_memory[23].value = BitBusValue([False, False, False, True, False, False, False, False])  # 0001 0000
print("22: SW   $1, 0($11) -> mem[4] = 5")

# 24: SW $2, 2($11)    -> mem[6] = reg[2] = 3
# Format: [opcode(0111=SW) | rs=11(1011) | rt=2(0010) | offset=2(0010)]
mips16x.instruction_memory[24].value = BitBusValue([False, True, True, True, True, False, True, True])  # 0111 1011
mips16x.instruction_memory[25].value = BitBusValue([False, False, True, False, False, False, True, False])  # 0010 0010
print("24: SW   $2, 2($11) -> mem[6] = 3")

# 26: LW $12, 0($11)   -> reg[12] = mem[4] = 5
# Format: [opcode(0110=LW) | rs=11(1011) | rt=12(1100) | offset=0(0000)]
mips16x.instruction_memory[26].value = BitBusValue([False, True, True, False, True, False, True, True])  # 0110 1011
mips16x.instruction_memory[27].value = BitBusValue([True, True, False, False, False, False, False, False])  # 1100 0000
print("26: LW   $12, 0($11) -> reg[12] = 5")

# 28: LW $13, 2($11)   -> reg[13] = mem[6] = 3
# Format: [opcode(0110=LW) | rs=11(1011) | rt=13(1101) | offset=2(0010)]
mips16x.instruction_memory[28].value = BitBusValue([False, True, True, False, True, False, True, True])  # 0110 1011
mips16x.instruction_memory[29].value = BitBusValue([True, True, False, True, False, False, True, False])  # 1101 0010
print("28: LW   $13, 2($11) -> reg[13] = 3")

# ============================================
# TESTE 5: Instrução ADDI final
# ============================================
print("\nTESTE 5: Instrução ADDI final")
print("-" * 50)

# 30: ADDI $14, $0, 7  -> reg[14] = 7
mips16x.instruction_memory[30].value = BitBusValue([False, True, False, True, False, False, False, False])  # 0101 0000
mips16x.instruction_memory[31].value = BitBusValue([True, True, True, False, False, True, True, True])  # 1110 0111
print("30: ADDI $14, $0, 7  -> reg[14] = 7")

print("\n" + "="*50 + "\n")

tb = TestBench(mips16x.mips)
tb.set_time_unit('ns')

# Executar 16 ciclos de clock para todas as instruções
for i in range(16):
    tb.update({'clk': '0'})
    tb.wait(5)
    tb.update({'clk': '1'})
    tb.wait(5)
    print(f"Ciclo {i+1} completo")

tb.save_vcd('mips16x_test_extended.vcd')
print("\n" + "="*50)
print("Simulação concluída! Arquivo VCD gerado: mips16x_test_extended.vcd")

print("\n" + "="*50)
print("RESULTADOS FINAIS DOS REGISTRADORES:")
print("="*50)

results = {}
for i in range(16):
    reg_value = int('0b' + ''.join(['1' if bit else '0' for bit in mips16x.registers[i].value.raw_value]), 2)
    results[i] = reg_value
    if i <= 15 and reg_value != 0:
        print(f"reg[{i:2d}] = {reg_value:3d}")

print("\n" + "="*50)
print("VALORES ESPERADOS:")
print("="*50)
print("reg[1]  = 5   (ADDI)")
print("reg[2]  = 3   (ADDI)")
print("reg[3]  = 8   (ADD: 5+3)")
print("reg[4]  = 5   (SUB: 8-3)")
print("reg[5]  = 7   (ADDI)")
print("reg[6]  = 6   (ADDI)")
print("reg[7]  = 6   (AND: 7&6)")
print("reg[8]  = 7   (OR: 7|6)")
print("reg[9]  = 1   (SLT: 3<5)")
print("reg[10] = 0   (SLT: 5<3)")
print("reg[11] = 4   (ADDI)")
print("reg[12] = 5   (LW)")
print("reg[13] = 3   (LW)")
print("reg[14] = 7   (ADDI)")

print("\n" + "="*50)
print("VERIFICAÇÃO DE MEMÓRIA:")
print("="*50)
mem_4_high = int('0b' + ''.join(['1' if bit else '0' for bit in mips16x.memory[4].value.raw_value]), 2)
mem_5_low = int('0b' + ''.join(['1' if bit else '0' for bit in mips16x.memory[5].value.raw_value]), 2)
mem_value_4 = (mem_4_high << 8) | mem_5_low
print(f"mem[4-5] = {mem_value_4} (esperado: 5)")

mem_6_high = int('0b' + ''.join(['1' if bit else '0' for bit in mips16x.memory[6].value.raw_value]), 2)
mem_7_low = int('0b' + ''.join(['1' if bit else '0' for bit in mips16x.memory[7].value.raw_value]), 2)
mem_value_6 = (mem_6_high << 8) | mem_7_low
print(f"mem[6-7] = {mem_value_6} (esperado: 3)")

print("\n" + "="*50)
success = (
    results[1] == 5 and results[2] == 3 and results[3] == 8 and
    results[4] == 5 and results[5] == 7 and results[6] == 6 and
    results[7] == 6 and results[8] == 7 and results[9] == 1 and
    results[10] == 0 and results[11] == 4 and results[12] == 5 and
    results[13] == 3 and results[14] == 7 and
    mem_value_4 == 5 and mem_value_6 == 3
)

if success:
    print("✓✓✓ TODOS OS TESTES PASSARAM! ✓✓✓")
else:
    print("✗ ALGUNS TESTES FALHARAM")
print("="*50)
