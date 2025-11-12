import struct

class Reader:
    """
    Tools for reading data types from an encoded SPY module.
    """

    def __init__(self, bytes: bytes, debug: bool):
        self.bytes = bytes
        self.pos = 0
        self.debug = debug

    def _read(self, fmt: str, size: int, annotation: str):
        """
        General method to read data based on a struct format and size.
        Advances the stream by the specified size.
        """
        unpacked = struct.unpack(fmt, self.bytes[self.pos: self.pos + size])
        if self.debug:
            print(f"read {fmt} {annotation} - {unpacked[0]} {self.bytes[self.pos: self.pos + size]}")
        self.pos += size
        return unpacked[0]

    def read_uint8(self, annotation="") -> int:
        """Read an 8-bit unsigned integer and advance the stream by 1 byte."""
        return self._read("!B", 1, annotation)

    def read_uint16(self, annotation="") -> int:
        """Read a 16-bit unsigned integer and advance the stream by 2 bytes."""
        return self._read("!H", 2, annotation)

    def read_uint32(self, annotation="") -> int:
        """Read a 32-bit unsigned integer and advance the stream by 4 bytes."""
        return self._read("!I", 4, annotation)

    def read_uint64(self, annotation="") -> int:
        """Read a 64-bit unsigned integer and advance the stream by 8 bytes."""
        return self._read("!Q", 8, annotation)

    def read_int8(self, annotation="") -> int:
        """Read an 8-bit signed integer and advance the stream by 1 byte."""
        return self._read("!b", 1, annotation)

    def read_int16(self, annotation="") -> int:
        """Read a 16-bit signed integer and advance the stream by 2 bytes."""
        return self._read("!h", 2, annotation)

    def read_int32(self, annotation="") -> int:
        """Read a 32-bit signed integer and advance the stream by 4 bytes."""
        return self._read("!i", 4, annotation)

    def read_int64(self, annotation="") -> int:
        """Read a 64-bit signed integer and advance the stream by 8 bytes."""
        return self._read("!q", 8, annotation)

    def read_float32(self, annotation="") -> float:
        """Read a 32-bit floating-point number and advance the stream by 4 bytes."""
        return self._read("!f", 4, annotation)

    def read_float64(self, annotation="") -> float:
        """Read a 64-bit floating-point number and advance the stream by 8 bytes."""
        return self._read("!d", 8, annotation)

    def read_varsize1632(self, annotation="") -> int:
        """
        Read a variable-sized 16- or 32-bit unsigned integer.
        If the value fits into 16 bits, read it as such; otherwise, read it as a 32-bit integer.
        Advance the stream by 2 or 4 bytes.
        """
        value = self._read("!H", 2, annotation)
        if value == 65535:
            value = self._read("!I", 4, annotation)
        return value

    def read_utf8(self, length: int, annotation="") -> str:
        """Read a UTF-8 encoded string of the specified length and advance the stream by that length."""
        unpacked = self.bytes[self.pos: self.pos + length].decode("utf-8")
        if self.debug:
            print(f"read utf8str {annotation} - {repr(unpacked)} {self.bytes[self.pos: self.pos + length]}")
        self.pos += length
        return unpacked

    def read_bytes(self, length: int, annotation="") -> bytes:
        """Read a sequence of raw bytes of the specified length and advance the stream by that length."""
        unpacked = self.bytes[self.pos: self.pos + length]
        if self.debug:
            print(f"read bytes {annotation} - {self.bytes[self.pos: self.pos + length]}")
        self.pos += length
        return unpacked