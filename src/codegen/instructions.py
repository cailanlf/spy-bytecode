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
    0x15: "LOAD_DEREF",
    0x16: "STORE_LOCAL",
    0x17: "STORE_GLOBAL",
    0x18: "STORE_NAME",
    0x19: "STORE_DEREF",

    0x1A: "MAKE_OBJECT",
    0x1B: "FREEZE",
    0x1C: "SEAL",

    0x20: "JUMP_FORWARD",
    0x21: "JUMP_BACKWARD",
    0x22: "JUMP_FORWARD_TRUE",
    0x23: "JUMP_FORWARD_FALSE",

    0x30: "CALL",
    0x31: "RETURN",
    0x32: "COPY_FREE_VARS",

    0x40: "ADD",
    0x41: "SUBTRACT",
    0x42: "MULTIPLY",
    0x43: "DIVIDE",

    0x50: "NEGATE",
    0x51: "POSITIVE",
    
    0x60: "EQ",
    0x61: "NEQ",
    0x62: "GT",
    0x63: "GTEQ",
    0x64: "LT",
    0x65: "LTEQ",
    0x66: "NOT",
    0x67: "AND",
    0x68: "OR",

    0x70: "LOCAL_SLOTS"
}

instruction_values = { v: k for k, v in instruction_names.items() }