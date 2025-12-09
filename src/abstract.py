from flote.backend.python.core.buses import BitBus, BitBusValue, Evaluator


class AbsAssignment(Evaluator):
    def __init__(self, assignment) -> None:
        self.assignment = assignment

    def evaluate(self):
        return self.assignment()


# Global variables to help with clock edge detection
# Dictionary to track clock state per component (identified by id)
clock_states: dict[int, tuple[bool, bool | None]] = {}  # {component_id: (current_clk, last_clk)}


def sum_bit_bus(a: BitBus, b: BitBus) -> BitBusValue:
    a_value = int('0b' + ''.join(['1' if bit else '0' for bit in a.value.raw_value]), 2)
    b_value = int('0b' + ''.join(['1' if bit else '0' for bit in b.value.raw_value]), 2)

    result = a_value + b_value
    result_bits = bin(result)[2:]  # Convert to binary and remove '0b'

    result_bools = [bit == '1' for bit in result_bits]
    return BitBusValue(result_bools)


def sub_bit_bus(a: BitBus, b: BitBus) -> BitBusValue:
    a_value = int('0b' + ''.join(['1' if bit else '0' for bit in a.value.raw_value]), 2)
    b_value = int('0b' + ''.join(['1' if bit else '0' for bit in b.value.raw_value]), 2)

    result = a_value - b_value
    result_bits = bin(result)[2:]  # Convert to binary and remove '0b'

    result_bools = [bit == '1' for bit in result_bits]
    return BitBusValue(result_bools)


def alu_out_op(a: BitBus, b: BitBus, sel: BitBus) -> BitBusValue:
    sel_str = ''.join(['1' if bit else '0' for bit in sel.value.raw_value])
    result = None

    a_value = int('0b' + ''.join(['1' if bit else '0' for bit in a.value.raw_value]), 2)
    b_value = int('0b' + ''.join(['1' if bit else '0' for bit in b.value.raw_value]), 2)

    match sel_str:
        case '000':
            result = sum_bit_bus(a, b)
        case '001':
            result = sub_bit_bus(a, b)
        case '010':
            result = a.value & b.value
        case '011':
            result = a.value | b.value
        case '100':
            result = BitBusValue(([False] * 15) + ([True] if a_value < b_value else [False]))

    assert result is not None, "ALU operation resulted in None"
    if len(result.raw_value) < 16:
        result = BitBusValue([False] * (16 - len(result.raw_value)) + result.raw_value)
    elif len(result.raw_value) > 16:
        result = BitBusValue(result.raw_value[-16:])
    return result


def update_reg(reg: BitBus, my_idx, idx: BitBus, in_data: BitBus, write_enable: BitBus, clk: BitBus):
    global clock_states

    component_id = id(reg)
    if component_id not in clock_states:
        clock_states[component_id] = (False, False)

    current_clk, last_clk = clock_states[component_id]

    if current_clk != clk.value.raw_value[0]:
        last_clk = current_clk
        current_clk = clk.value.raw_value[0]
        clock_states[component_id] = (current_clk, last_clk)

    if current_clk and not last_clk:
        if write_enable.value.raw_value[0] and my_idx == int(
            '0b' + ''.join('1' if bit else '0' for bit in idx.value.raw_value),
            2,
        ):
            return BitBusValue(in_data.value.raw_value)

    return BitBusValue(reg.value.raw_value)
def update_mem(mem: BitBus, my_idx, addr: BitBus, write_data: BitBus, write_enable: BitBus, clk: BitBus):
    """Atualiza uma posição da memória (byte) na borda de subida do clock se write_enable estiver ativo"""
    global clock_states

    component_id = id(mem)
    if component_id not in clock_states:
        clock_states[component_id] = (False, False)

    current_clk, last_clk = clock_states[component_id]

    if current_clk != clk.value.raw_value[0]:
        last_clk = current_clk
        current_clk = clk.value.raw_value[0]
        clock_states[component_id] = (current_clk, last_clk)    # Escrita na borda de subida do clock
    if current_clk and not last_clk:
        if write_enable.value.raw_value[0]:  # Se write_enable está ativo
            addr_value = int('0b' + ''.join('1' if bit else '0' for bit in addr.value.raw_value), 2)

            # Escreve nos 2 bytes (palavra de 16 bits dividida em 2 bytes)
            if my_idx == addr_value:
                # Byte mais significativo (primeiros 8 bits)
                return BitBusValue(write_data.value.raw_value[0:8])
            elif my_idx == addr_value + 1:
                # Byte menos significativo (últimos 8 bits)
                return BitBusValue(write_data.value.raw_value[8:16])

    return BitBusValue(mem.value.raw_value)


def read_mem(memory_array, addr: BitBus) -> BitBusValue:
    """Lê da memória de forma assíncrona (combina 2 bytes em uma palavra de 16 bits)"""
    addr_value = int('0b' + ''.join('1' if bit else '0' for bit in addr.value.raw_value), 2)
    # Limita o endereço ao tamanho da memória
    addr_value = addr_value % len(memory_array)

    # Lê 2 bytes consecutivos (byte_addr e byte_addr+1) e combina em 16 bits
    byte1 = memory_array[addr_value].value.raw_value  # Byte mais significativo
    byte2_addr = (addr_value + 1) % len(memory_array)
    byte2 = memory_array[byte2_addr].value.raw_value  # Byte menos significativo

    # Combina os dois bytes: [byte1 (8 bits) | byte2 (8 bits)] = 16 bits
    return BitBusValue(byte1 + byte2)


def mux_2to1(sel: BitBus, in0: BitBus, in1: BitBus) -> BitBusValue:
    """Multiplexador 2 para 1: se sel=0 retorna in0, se sel=1 retorna in1"""
    if sel.value.raw_value[0]:  # sel == 1
        return BitBusValue(in1.value.raw_value)
    else:  # sel == 0
        return BitBusValue(in0.value.raw_value)


def update_pc(pc: BitBus, clk: BitBus) -> BitBusValue:
    """Atualiza o PC na borda de subida do clock (PC = PC + 2)"""
    global clock_states

    component_id = id(pc)
    if component_id not in clock_states:
        clock_states[component_id] = (False, False)

    current_clk, last_clk = clock_states[component_id]

    if current_clk != clk.value.raw_value[0]:
        last_clk = current_clk
        current_clk = clk.value.raw_value[0]
        clock_states[component_id] = (current_clk, last_clk)    # Incrementa PC na borda de subida do clock (PC = PC + 2)
    if current_clk and not last_clk:
        pc_value = int('0b' + ''.join('1' if bit else '0' for bit in pc.value.raw_value), 2)
        new_pc = pc_value + 2
        new_pc_bits = bin(new_pc)[2:]
        result = BitBusValue([bit == '1' for bit in new_pc_bits])

        # Ajusta para 16 bits
        if len(result.raw_value) < 16:
            result = BitBusValue([False] * (16 - len(result.raw_value)) + result.raw_value)
        elif len(result.raw_value) > 16:
            result = BitBusValue(result.raw_value[-16:])

        return result

    return BitBusValue(pc.value.raw_value)


def extract_opcode(instruction: BitBus) -> BitBusValue:
    """Extrai os 4 bits mais significativos (opcode) da instrução de 16 bits"""
    return BitBusValue(instruction.value.raw_value[0:4])


def extract_rs(instruction: BitBus) -> BitBusValue:
    """Extrai bits [15:12] como rs (4 bits)"""
    return BitBusValue(instruction.value.raw_value[4:8])


def extract_rt(instruction: BitBus) -> BitBusValue:
    """Extrai bits [11:8] como rt (4 bits)"""
    return BitBusValue(instruction.value.raw_value[8:12])


def extract_rd(instruction: BitBus) -> BitBusValue:
    """Extrai bits [7:4] como rd (4 bits)"""
    return BitBusValue(instruction.value.raw_value[12:16])


def mux_4bit_2to1(sel: BitBus, in0: BitBus, in1: BitBus) -> BitBusValue:
    """Multiplexador 2 para 1 para sinais de 4 bits (usado para selecionar entre rt e rd)"""
    if sel.value.raw_value[0]:  # sel == 1
        return BitBusValue(in1.value.raw_value)
    else:  # sel == 0
        return BitBusValue(in0.value.raw_value)


def control_unit(opcode: BitBus) -> tuple[BitBusValue, BitBusValue, BitBusValue, BitBusValue, BitBusValue, BitBusValue, BitBusValue, BitBusValue]:
    """Unidade de controle que gera sinais baseado no opcode

    Retorna: (reg_dst, alu_src, mem_to_reg, rf_write_enable, mem_write_enable, branch, alu_op[3 bits], jump)

    Instruções:
    0000 - ADD  (tipo R): reg_dst=1, alu_src=0, mem_to_reg=0, reg_write=1, mem_write=0, branch=0, alu_op=000, jump=0
    0001 - SUB  (tipo R): reg_dst=1, alu_src=0, mem_to_reg=0, reg_write=1, mem_write=0, branch=0, alu_op=001, jump=0
    0010 - AND  (tipo R): reg_dst=1, alu_src=0, mem_to_reg=0, reg_write=1, mem_write=0, branch=0, alu_op=010, jump=0
    0011 - OR   (tipo R): reg_dst=1, alu_src=0, mem_to_reg=0, reg_write=1, mem_write=0, branch=0, alu_op=011, jump=0
    0100 - SLT  (tipo R): reg_dst=1, alu_src=0, mem_to_reg=0, reg_write=1, mem_write=0, branch=0, alu_op=100, jump=0
    0101 - ADDI (tipo I): reg_dst=0, alu_src=1, mem_to_reg=0, reg_write=1, mem_write=0, branch=0, alu_op=000, jump=0
    0110 - LW   (tipo I): reg_dst=0, alu_src=1, mem_to_reg=1, reg_write=1, mem_write=0, branch=0, alu_op=000, jump=0
    0111 - SW   (tipo I): reg_dst=X, alu_src=1, mem_to_reg=X, reg_write=0, mem_write=1, branch=0, alu_op=000, jump=0
    1000 - BEQ  (tipo I): reg_dst=X, alu_src=0, mem_to_reg=X, reg_write=0, mem_write=0, branch=1, alu_op=001, jump=0
    1001 - JUMP (tipo J): reg_dst=X, alu_src=X, mem_to_reg=X, reg_write=0, mem_write=0, branch=0, alu_op=XXX, jump=1
    """
    opcode_str = ''.join(['1' if bit else '0' for bit in opcode.value.raw_value])

    # Valores padrão (NOP)
    reg_dst = False
    alu_src = False
    mem_to_reg = False
    rf_write_enable = False
    mem_write_enable = False
    branch = False
    alu_op = [False, False, False]
    jump = False

    match opcode_str:
        case '0000':  # ADD
            reg_dst = True
            alu_src = False
            mem_to_reg = False
            rf_write_enable = True
            mem_write_enable = False
            branch = False
            alu_op = [False, False, False]  # 000
            jump = False

        case '0001':  # SUB
            reg_dst = True
            alu_src = False
            mem_to_reg = False
            rf_write_enable = True
            mem_write_enable = False
            branch = False
            alu_op = [False, False, True]  # 001
            jump = False

        case '0010':  # AND
            reg_dst = True
            alu_src = False
            mem_to_reg = False
            rf_write_enable = True
            mem_write_enable = False
            branch = False
            alu_op = [False, True, False]  # 010
            jump = False

        case '0011':  # OR
            reg_dst = True
            alu_src = False
            mem_to_reg = False
            rf_write_enable = True
            mem_write_enable = False
            branch = False
            alu_op = [False, True, True]  # 011
            jump = False

        case '0100':  # SLT
            reg_dst = True
            alu_src = False
            mem_to_reg = False
            rf_write_enable = True
            mem_write_enable = False
            branch = False
            alu_op = [True, False, False]  # 100
            jump = False

        case '0101':  # ADDI
            reg_dst = False
            alu_src = True
            mem_to_reg = False
            rf_write_enable = True
            mem_write_enable = False
            branch = False
            alu_op = [False, False, False]  # 000
            jump = False

        case '0110':  # LW
            reg_dst = False
            alu_src = True
            mem_to_reg = True
            rf_write_enable = True
            mem_write_enable = False
            branch = False
            alu_op = [False, False, False]  # 000
            jump = False

        case '0111':  # SW
            reg_dst = False  # Don't care
            alu_src = True
            mem_to_reg = False  # Don't care
            rf_write_enable = False
            mem_write_enable = True
            branch = False
            alu_op = [False, False, False]  # 000
            jump = False

        case '1000':  # BEQ
            reg_dst = False  # Don't care
            alu_src = False
            mem_to_reg = False  # Don't care
            rf_write_enable = False
            mem_write_enable = False
            branch = True
            alu_op = [False, False, True]  # 001 (subtração para comparar)
            jump = False

        case '1001':  # JUMP
            reg_dst = False  # Don't care
            alu_src = False  # Don't care
            mem_to_reg = False  # Don't care
            rf_write_enable = False
            mem_write_enable = False
            branch = False
            alu_op = [False, False, False]  # Don't care
            jump = True

    return (
        BitBusValue([reg_dst]),
        BitBusValue([alu_src]),
        BitBusValue([mem_to_reg]),
        BitBusValue([rf_write_enable]),
        BitBusValue([mem_write_enable]),
        BitBusValue([branch]),
        BitBusValue(alu_op),
        BitBusValue([jump])
    )


def sign_extend_4to16(value_4bit: BitBus) -> BitBusValue:
    """Extensor de sinal: estende 4 bits para 16 bits com extensão de sinal"""
    bits = value_4bit.value.raw_value
    # Pega o bit de sinal (MSB)
    sign_bit = bits[0]
    # Estende o bit de sinal para os 12 bits mais significativos
    extended = [sign_bit] * 12 + bits
    return BitBusValue(extended)


def mux_alu_src(sel: BitBus, reg_data: BitBus, immediate: BitBus) -> BitBusValue:
    """Multiplexador para entrada B da ALU: seleciona entre registrador ou imediato"""
    if sel.value.raw_value[0]:  # sel == 1, usa imediato
        return BitBusValue(immediate.value.raw_value)
    else:  # sel == 0, usa dado do registrador
        return BitBusValue(reg_data.value.raw_value)


def shift_left_1(value: BitBus) -> BitBusValue:
    """Desloca o valor 1 bit à esquerda (equivalente a multiplicar por 2)"""
    bits = value.value.raw_value
    # Desloca para esquerda e adiciona 0 no bit menos significativo
    shifted = bits[1:] + [False]
    return BitBusValue(shifted)


def add_bus(a: BitBus, b: BitBus) -> BitBusValue:
    """Soma dois sinais de 16 bits"""
    a_value = int('0b' + ''.join(['1' if bit else '0' for bit in a.value.raw_value]), 2)
    b_value = int('0b' + ''.join(['1' if bit else '0' for bit in b.value.raw_value]), 2)

    result = a_value + b_value
    result_bits = bin(result)[2:]
    result_bools = [bit == '1' for bit in result_bits]

    # Ajusta para 16 bits
    if len(result_bools) < 16:
        result_bools = [False] * (16 - len(result_bools)) + result_bools
    elif len(result_bools) > 16:
        result_bools = result_bools[-16:]

    return BitBusValue(result_bools)


def concat_jump_addr(pc_upper: BitBus, instr_field: BitBus) -> BitBusValue:
    """Concatena PC[15:12] com campo da instrução deslocado 1 bit à esquerda
    PC[15:12] | instr_field[11:0] << 1"""
    pc_bits = pc_upper.value.raw_value[0:4]  # 4 bits superiores do PC
    instr_bits = instr_field.value.raw_value  # Campo da instrução (12 bits)

    # Desloca instrução 1 bit à esquerda (adiciona 0 no LSB)
    shifted_instr = instr_bits[1:] + [False]  # Agora tem 12 bits

    # Concatena: PC[15:12] (4 bits) + shifted_instr (12 bits) = 16 bits
    return BitBusValue(pc_bits + shifted_instr)


def alu_zero(alu_result: BitBus) -> BitBusValue:
    """Gera sinal zero da ALU (1 bit): true se resultado for zero"""
    is_zero = all(not bit for bit in alu_result.value.raw_value)
    return BitBusValue([is_zero])


def update_pc_reg(pc: BitBus, next_pc: BitBus, clk: BitBus) -> BitBusValue:
    """Atualiza o PC na borda de subida do clock com o valor de next_pc"""
    global clock_states

    component_id = id(pc)
    if component_id not in clock_states:
        clock_states[component_id] = (False, False)

    current_clk, last_clk = clock_states[component_id]

    if current_clk != clk.value.raw_value[0]:
        last_clk = current_clk
        current_clk = clk.value.raw_value[0]
        clock_states[component_id] = (current_clk, last_clk)    # Atualiza PC na borda de subida do clock
    if current_clk and not last_clk:
        return BitBusValue(next_pc.value.raw_value)

    return BitBusValue(pc.value.raw_value)
