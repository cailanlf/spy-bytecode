def write_int_as_uint8(bytes: bytearray, to_write: int):
    bytes.extend(to_write.to_bytes(1, byteorder='big', signed=False))

def write_int_as_uint16(bytes: bytearray, to_write: int):
    bytes.extend(to_write.to_bytes(2, byteorder='big', signed=False))