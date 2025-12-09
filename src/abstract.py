from flote.backend.python.core.buses import BitBus, BitBusValue, Evaluator


class AbsAssignment(Evaluator):
    def __init__(self, assignment) -> None:
        self.assignment = assignment

    def evaluate(self):
        return self.assignment()


# Global variables to help with clock edge detection
current_clk = False
last_clk = None


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


def update_reg(reg: BitBus, my_idx, idx: BitBus, in_data: BitBus, clk: BitBus):
    global last_clk
    global current_clk

    if last_clk is None:
        last_clk = False

    if current_clk != clk.value.raw_value[0]:
        last_clk = current_clk
        current_clk = clk.value.raw_value[0]

    if current_clk and not last_clk:
        if my_idx == int(
            '0b' + ''.join('1' if bit else '0' for bit in idx.value.raw_value),
            2,
        ):
            return BitBusValue(in_data.value.raw_value)

    return BitBusValue(reg.value.raw_value)


def update_mem(mem: BitBus, my_idx, addr: BitBus, write_data: BitBus, write_enable: BitBus, clk: BitBus):
    """Atualiza uma posição da memória (byte) na borda de subida do clock se write_enable estiver ativo"""
    global last_clk
    global current_clk

    if last_clk is None:
        last_clk = False

    if current_clk != clk.value.raw_value[0]:
        last_clk = current_clk
        current_clk = clk.value.raw_value[0]

    # Escrita na borda de subida do clock
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
    global last_clk
    global current_clk

    if last_clk is None:
        last_clk = False

    if current_clk != clk.value.raw_value[0]:
        last_clk = current_clk
        current_clk = clk.value.raw_value[0]

    # Incrementa PC na borda de subida do clock (PC = PC + 2)
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
