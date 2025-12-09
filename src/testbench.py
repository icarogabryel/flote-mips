from flote.testbench import TestBench

import mips16x

input_values = [
    # Teste 1: Soma (reg[0] + reg[1]) e salva no reg[4]
    # mem_to_reg=0 (usa saída da ALU)
    {
        'rf_write_enable': '1',
        'rf_read_addr1': '0000',
        'rf_read_addr2': '0001',
        'rf_write_addr': '0100',
        'alu_op': '000',
        'mem_to_reg': '0',
        'mem_write_enable': '0',
    },

    # Teste 2: AND (reg[0] & reg[1]) e salva no reg[5]
    # mem_to_reg=0 (usa saída da ALU)
    {
        'rf_write_enable': '1',
        'rf_read_addr1': '0000',
        'rf_read_addr2': '0001',
        'rf_write_addr': '0101',
        'alu_op': '010',
        'mem_to_reg': '0',
        'mem_write_enable': '0',
    },

    # Teste 3: Escreve reg[1] na memória no endereço calculado (reg[0] + reg[1])
    # mem_write_enable=1 para escrever na memória
    {
        'rf_write_enable': '0',
        'rf_read_addr1': '0000',
        'rf_read_addr2': '0001',
        'rf_write_addr': '0000',
        'alu_op': '000',
        'mem_to_reg': '0',
        'mem_write_enable': '1',
    },

    # Teste 4: Lê da memória e salva no reg[6]
    # mem_to_reg=1 (usa saída da memória)
    {
        'rf_write_enable': '1',
        'rf_read_addr1': '0000',
        'rf_read_addr2': '0001',
        'rf_write_addr': '0110',
        'alu_op': '000',
        'mem_to_reg': '1',
        'mem_write_enable': '0',
    },
]

tb = TestBench(mips16x.mips)
tb.set_time_unit('ns')

for input_set in input_values:
    input_set['clk'] = '0'
    tb.update(input_set)
    tb.wait(5)
    tb.update({'clk': '1'})
    tb.wait(5)

tb.save_vcd('mips16x_test.vcd')
