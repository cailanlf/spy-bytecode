from typing import Optional, Self
from codegen.consts import *
from parsenodes import *
import codegen.writer as writer
from codegen.reader import Reader
from codegen.instructions import instruction_values, instruction_names

class Block():
    """
    Represents a compilation unit. These are currently modules and function bodies.
    """
    
    global_names: list[str]
    local_names: list[str]
    names: list[str]
    body: bytearray
    context: Literal['block', 'module']

    consts: list[Const]

    def __init__(self, context: Literal['block', 'module']):
        self.context = context
        self.global_names = []
        self.local_names = []
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
        
    def get_name_index(self, name: str) -> int:
        """
        Gets or inserts a name into the names list.
        """

        try:
            return self.names.index(name)
        except ValueError:
            self.names.append(name)
            return len(self.names) - 1
        
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

    def emit_load_attr(self):
        """
        Emit a `LOAD_ATTR` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["LOAD_ATTR"])

    def emit_store_name(self, index: int):
        """
        Emit a `STORE_NAME` instruction.
        
        Args:
            index (int): A `uint16`-coercible index into the names table.
        """
                
        writer.write_int_as_uint8(self.body, instruction_values["STORE_NAME"])
        writer.write_int_as_uint16(self.body, index)

    def emit_store_attr(self):
        """
        Emit a `STORE_ATTR` instruction.
        """

        writer.write_int_as_uint8(self.body, instruction_values["STORE_ATTR"])

    def emit_call(self, argc: int):
        """
        Emit a `CALL` instruction.
        
        Args:
            index (int): A `uint16`-coercible number of arguments that were provided to the function.
        """

        writer.write_int_as_uint8(self.body, instruction_values["CALL"])
        writer.write_int_as_uint16(self.body, argc)

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
        
    def pretty_print(self):
        reader = Reader(self.body, debug=False)
        while reader.pos < len(self.body):
            print(" ".ljust(8), end="")
            instruction = reader.read_uint8()
            name = instruction_names[instruction]
            print(name.ljust(15), end=" ")

            if name == "LOAD_CONST" or name == "STORE_CONST":
                arg = reader.read_uint16()
                print(arg, end=" ")
                print(f"({self.consts[arg]})", end="")
            if name == "LOAD_NAME" or name == "STORE_NAME":
                arg = reader.read_uint16()
                print(arg, end=" ")
                print(f"({self.names[arg]})", end="")
            elif name == "CALL":
                arg = str(reader.read_uint16())
                print(arg, end="")
                pass
            print()

def compile_program(root: ProgramNode):
    block = Block('module')
    for statement in root.body.statements:
        generate_bytecode(statement, block)
        block.emit_nop()
    return block

def generate_bytecode(node: Node, block: Block):
    match node:
        case ProgramNode():
            raise NotImplementedError("Not implemented for ProgramNodes; please use compile_program")
        
        case NumberLiteralNode():
            idx = block.get_const_index(IntegerConst(node.value))
            block.emit_load_const(idx)

        case StringLiteralNode():
            idx = block.get_const_index(StringConst(node.value))
            block.emit_load_const(idx)

        case NoneLiteralNode():
            idx = block.get_const_index(NoneConst())
            block.emit_load_const(idx)
        
        case BoolLiteralNode():
            idx = block.get_const_index(BoolConst(0 if node.value == False else 1))
            block.emit_load_const(idx)

        case ObjectLiteralNode():
            block.emit_make_object()

            for entry in node.entries:
                generate_bytecode(entry, block)

            if node.modifier == "frozen":
                block.emit_freeze()
            elif node.modifier == "sealed":
                block.emit_seal()

        case ObjectLiteralEntryNode():
            generate_bytecode(node.name, block)
            generate_bytecode(node.value, block)
            block.emit_store_attr()

        case IdentifierNode():
            # if we're at a module level:
            # - always use LOAD_NAME
            # if we're at a function level:
            # - check if the value is declared as a local in the current scope
            if block.context == 'module':
                idx = block.get_name_index(node.value)
                block.emit_load_name(idx)

        case LetStatementNode():
            left = node.left

            if type(left) is not IdentifierNode:
                raise Exception("Left side of let statement must be an identifier")
            
            idx = block.get_name_index(left.value)
            generate_bytecode(node.right, block)
            block.emit_store_name(idx)

        case ExpressionStatementNode():
            expr = node.expression

            generate_bytecode(expr, block)
            block.emit_pop()

        case CallExpressionNode():
            generate_bytecode(node.callee, block)
            for arg in node.arguments:
                generate_bytecode(arg, block)
            block.emit_call(len(node.arguments))

        case BinaryExpressionNode():
            match node.operator:
                case '+':
                    generate_bytecode(node.left, block)
                    generate_bytecode(node.right, block)
                    block.emit_add()
                case '-':
                    generate_bytecode(node.left, block)
                    generate_bytecode(node.right, block)
                    block.emit_subtract()
                case '*':
                    generate_bytecode(node.left, block)
                    generate_bytecode(node.right, block)
                    block.emit_multiply()
                case '/':
                    generate_bytecode(node.left, block)
                    generate_bytecode(node.right, block)
                    block.emit_divide()
                case '=':
                    if type(node.left) is IdentifierNode:
                        if block.context == "module":
                            idx = block.get_name_index(node.left.value)
                            generate_bytecode(node.right, block)
                            block.emit_store_name(idx)
                        else:
                            raise NotImplementedError("Not implemented for this context")
                    elif type(node.left) is IndexExpressionNode:
                        generate_bytecode(node.left, block)
                        generate_bytecode(node.right, block)
                        block.emit_store_attr()
                    else:
                        raise NotImplementedError("Invalid left hand side for assignment expression")

                case _:
                    raise NotImplementedError(f"Not implemented for binary operation {node.operator}")

        case IndexExpressionNode():
            generate_bytecode(node.indexee, block)
            generate_bytecode(node.index, block)
            block.emit_load_attr()

        case _:
            raise NotImplementedError(f"Not implemented for {type(node)}")