from typing import Literal

import codegen.writer as writer
from codegen.reader import Reader
from codegen.consts import Const, FunctionLiteralConst
from codegen.instructions import instruction_values, instruction_names

class Block():
    """
    Represents a compilation unit. These are currently modules and function bodies.
    """
    
    global_names: list[str]
    local_names: list[str]
    names: list[str]
    body: bytearray
    context: Literal['function', 'module']

    consts: list[Const]

    def __init__(self, context: Literal['function', 'module']):
        self.context = context

        # Names of global variables used within this block
        self.global_names = []

        # Names of local variables used within this block
        self.local_names: list[str] = []

        # Names of captured variables (closed over) within this block
        self.cell_names: list[str] = []

        # Names of free variables (captured from outer scope) within this block
        self.free_names: list[str] = []
        self.names = []
        self.consts = []
        self.body = bytearray()

    def get_const_index(self, const: Const) -> int:
        """
        Gets or inserts a constant into the consts list representing the given constant.
        """

        try:
            return self.consts.index(const)
        except ValueError:
            self.consts.append(const)
            return len(self.consts) - 1
        
    def get_local_index(self, name: str) -> int | None:
        """
        Gets a local from the locals list or None if it does not exist
        """

        try:
            return self.local_names.index(name)
        except ValueError:
            return None
        
    def get_insert_local_index(self, name: str) -> int:
        """
        Gets or inserts a local into the locals list.
        """

        try:
            return self.names.index(name)
        except ValueError:
            self.local_names.append(name)
            return len(self.local_names) - 1

    def get_insert_name_index(self, name: str) -> int:
        """
        Gets or inserts a name into the names list.
        """

        try:
            return self.names.index(name)
        except ValueError:
            self.names.append(name)
            return len(self.names) - 1
            
    def get_name_index(self, name: str) -> int | None:
        """
        Gets a name from the names list or None if it does not exist
        """

        try:
            return self.names.index(name)
        except ValueError:
            return None
        
    def get_deref_index(self, name: str) -> int | None:
        """
        Gets a name from cell_vars OR free_vars or None if it does not exist
        """

        try:
            return self.cell_names.index(name)
        except ValueError:
            try:
                return self.free_names.index(name) + len(self.cell_names)
            except ValueError:
                return None
        
    def emit_nop(self):
        """
        Emit a `NOP` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["NOP"])

    def emit_pop(self):
        """
        Emit a `POP` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["POP"])

    def emit_load_const(self, index: int):
        """
        Emit a `LOAD_CONST` instruction.
        
        Args:
            index (int): A `uint16`-coercible index into the constants table.
        """

        writer.write_int_as_uint8(self.body, instruction_values["LOAD_CONST"])
        writer.write_int_as_uint16(self.body, index)

    def emit_load_name(self, index: int):
        """
        Emit a `LOAD_NAME` instruction.
        
        Args:
            index (int): A `uint16`-coercible index into the names table.
        """
                
        writer.write_int_as_uint8(self.body, instruction_values["LOAD_NAME"])
        writer.write_int_as_uint16(self.body, index)

    def emit_load_local(self, index: int):
        """
        Emit a `LOAD_LOCAL` instruction.
        
        Args:
            index (int): A `uint16`-coercible index into the names table.
        """
                
        writer.write_int_as_uint8(self.body, instruction_values["LOAD_LOCAL"])
        writer.write_int_as_uint16(self.body, index)

    def emit_load_attr(self):
        """
        Emit a `LOAD_ATTR` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["LOAD_ATTR"])

    def emit_load_deref(self, index: int):
        """
        Emit a `LOAD_DEREF` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["LOAD_DEREF"])
        writer.write_int_as_uint16(self.body, index)

    def emit_store_name(self, index: int):
        """
        Emit a `STORE_NAME` instruction.
        
        Args:
            index (int): A `uint16`-coercible index into the names table.
        """
                
        writer.write_int_as_uint8(self.body, instruction_values["STORE_NAME"])
        writer.write_int_as_uint16(self.body, index)

    def emit_store_local(self, index: int):
        """
        Emit a `STORE_LOCAL` instruction.
        
        Args:
            index (int): A `uint16`-coercible index into the locals table.
        """
                
        writer.write_int_as_uint8(self.body, instruction_values["STORE_LOCAL"])
        writer.write_int_as_uint16(self.body, index)

    def emit_store_attr(self):
        """
        Emit a `STORE_ATTR` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["STORE_ATTR"])

    def emit_store_deref(self, index: int):
        """
        Emit a `STORE_DEREF` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["STORE_DEREF"])
        writer.write_int_as_uint16(self.body, index)

    def emit_call(self, argc: int):
        """
        Emit a `CALL` instruction.
        
        Args:
            index (int): A `uint16`-coercible number of arguments that were provided to the function.
        """

        writer.write_int_as_uint8(self.body, instruction_values["CALL"])
        writer.write_int_as_uint16(self.body, argc)

    def emit_return(self):
        """
        Emit a `RETURN` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["RETURN"])

    def emit_copy_free_vars(self):
        """
        Emit a `COPY_FREE_VARS` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["COPY_FREE_VARS"])

    def emit_make_object(self):
        """
        Emit a `MAKE_OBJECT` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["MAKE_OBJECT"])

    def emit_freeze(self):
        """
        Emit a `FREEZE` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["FREEZE"])

    def emit_seal(self):
        """
        Emit a `SEAL` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["SEAL"])

    def emit_add(self):
        """
        Emit an `ADD` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["ADD"])

    def emit_subtract(self):
        """
        Emit a `SUBTRACT` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["SUBTRACT"])

    def emit_multiply(self):
        """
        Emit a `MULTIPLY` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["MULTIPLY"])

    def emit_divide(self):
        """
        Emit a `DIVIDE` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["DIVIDE"])

    def emit_negate(self):
        """
        Emit a `NEGATE` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["NEGATE"])

    def emit_positive(self):
        """
        Emit a `POSITIVE` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["POSITIVE"])

    def emit_eq(self):
        """
        Emit an `EQ` instruction
        """

        writer.write_int_as_uint8(self.body, instruction_values["EQ"])

    def emit_neq(self):
        """
        Emit a `NEQ` instruction
        """

        writer.write_int_as_uint8(self.body, instruction_values["NEQ"])

    def emit_lt(self):
        """
        Emit a `LT` instruction
        """

        writer.write_int_as_uint8(self.body, instruction_values["LT"])

    def emit_lteq(self):
        """
        Emit a `LTEQ` instruction
        """

        writer.write_int_as_uint8(self.body, instruction_values["LTEQ"])

    def emit_gt(self):
        """
        Emit a `GT` instruction
        """

        writer.write_int_as_uint8(self.body, instruction_values["GT"])

    def emit_gteq(self):
        """
        Emit a `GTEQ` instruction
        """

        writer.write_int_as_uint8(self.body, instruction_values["GTEQ"])

    def emit_and(self):
        """
        Emit an `AND` instruction
        """

        writer.write_int_as_uint8(self.body, instruction_values["AND"])

    def emit_or(self):
        """
        Emit an `OR` instruction
        """

        writer.write_int_as_uint8(self.body, instruction_values["OR"])

    def emit_not(self):
        """
        Emit a `NOT` instruction
        """

        writer.write_int_as_uint8(self.body, instruction_values["NOT"])

    def emit_jump_forward(self, offset: int):
        """
        Emit a `JUMP_FORWARD` instruction with the given offset.
        """

        writer.write_int_as_uint8(self.body, instruction_values["JUMP_FORWARD"])
        writer.write_int_as_uint16(self.body, offset)

    def emit_jump_forward_true(self, offset: int):
        """
        Emit a `JUMP_FORWARD_TRUE` instruction with the given offset.
        """

        writer.write_int_as_uint8(self.body, instruction_values["JUMP_FORWARD_TRUE"])
        writer.write_int_as_uint16(self.body, offset)

    def emit_jump_forward_false(self, offset: int):
        """
        Emit a `JUMP_FORWARD_FALSE` instruction with the given offset.
        """

        writer.write_int_as_uint8(self.body, instruction_values["JUMP_FORWARD_FALSE"])
        writer.write_int_as_uint16(self.body, offset)
        
    def pretty_print(self):
        reader = Reader(self.body, debug=False)
        while reader.pos < len(self.body):
            print(f"{reader.pos:04X}".ljust(8), end="")
            instruction = reader.read_uint8()
            name = instruction_names[instruction]
            print(name.ljust(20), end=" ")

            if name == "LOAD_CONST" or name == "STORE_CONST":
                arg = reader.read_uint16()
                print(arg, end=" ")
                print(f"({self.consts[arg]})", end="")
            if name == "LOAD_NAME" or name == "STORE_NAME":
                arg = reader.read_uint16()
                print(arg, end=" ")
                print(f"({self.names[arg]})", end="")
            if name == "LOAD_LOCAL" or name == "STORE_LOCAL":
                arg = reader.read_uint16()
                print(arg, end=" ")
                print(f"({self.local_names[arg]})", end="")
            if name == "LOAD_DEREF" or name == "STORE_DEREF":
                arg = reader.read_uint16()
                print(arg, end=" ")
                if arg >= len(self.cell_names):
                    print(f"({self.free_names[arg - len(self.cell_names)]})", end="")
                else:
                    print(f"({self.cell_names[arg]})", end="")
            if name == "JUMP_FORWARD" or name == "JUMP_BACKWARD" \
                or name == "JUMP_FORWARD_TRUE" or name == "JUMP_FORWARD_FALSE":
                arg = reader.read_uint16()
                print(arg, end=" ")
                print(f"({reader.pos + arg - 3:04X})", end=" ")
            elif name == "CALL":
                arg = str(reader.read_uint16())
                print(arg, end="")
                pass
            print()
        
        for i, const in enumerate(self.consts):
            if type(const) is FunctionLiteralConst:
                print()
                print(f"FUNCTION CONSTANT AT ({i})")
                const.block.pretty_print()
