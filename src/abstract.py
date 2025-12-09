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

    print(f'clk={current_clk}, last_clk={last_clk}')
    if current_clk and not last_clk:
        if my_idx == int(
            '0b' + ''.join('1' if bit else '0' for bit in idx.value.raw_value),
            2,
        ):
            return BitBusValue(in_data.value.raw_value)

    return BitBusValue(reg.value.raw_value)


def update_mem(mem: BitBus, my_idx, addr: BitBus, write_data: BitBus, write_enable: BitBus, clk: BitBus):
    """Atualiza uma posição da memória na borda de subida do clock se write_enable estiver ativo"""
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
            if my_idx == addr_value:
                return BitBusValue(write_data.value.raw_value)

    return BitBusValue(mem.value.raw_value)


def read_mem(memory_array, addr: BitBus) -> BitBusValue:
    """Lê da memória de forma assíncrona"""
    addr_value = int('0b' + ''.join('1' if bit else '0' for bit in addr.value.raw_value), 2)
    # Limita o endereço ao tamanho da memória
    addr_value = addr_value % len(memory_array)
    return BitBusValue(memory_array[addr_value].value.raw_value)


def mux_2to1(sel: BitBus, in0: BitBus, in1: BitBus) -> BitBusValue:
    """Multiplexador 2 para 1: se sel=0 retorna in0, se sel=1 retorna in1"""
    if sel.value.raw_value[0]:  # sel == 1
        return BitBusValue(in1.value.raw_value)
    else:  # sel == 0
        return BitBusValue(in0.value.raw_value)
