instruction_names = {
    0x00: "NOP",
    0x01: "POP",
    0x02: "DUP",
    0x03: "SWAP",

    0x10: "LOAD_LOCAL",
    0x11: "LOAD_GLOBAL",
    0x12: "LOAD_NAME",
    0x13: "LOAD_ATTR",
    0x14: "LOAD_CONST",
    0x15: "STORE_LOCAL",
    0x16: "STORE_GLOBAL",
    0x17: "STORE_NAME",
    0x18: "STORE_ATTR",

    0x19: "MAKE_OBJECT",
    0x1A: "FREEZE",
    0x1B: "SEAL",

    0x20: "JUMP_FORWARD",
    0x21: "JUMP_BACKWARD",
    0x22: "JUMP_IF_TRUE",
    0x23: "JUMP_IF_FALSE",

    0x30: "CALL",
    0x31: "RETURN",

    0x40: "ADD",
    0x41: "SUBTRACT",
    0x42: "MULTIPLY",
    0x43: "DIVIDE",
}

instruction_values = { v: k for k, v in instruction_names.items() }