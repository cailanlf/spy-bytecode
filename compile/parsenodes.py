
from dataclasses import dataclass
from typing import List, Union, Optional, Literal
from tokens import UnaryOperator, BinaryOperator

@dataclass
class ProgramNode:
    body: "BlockNode"

@dataclass
class LetStatementNode:
    left: "Node"
    right: "Node"

@dataclass
class ExpressionStatementNode:
    expression: "Node"

@dataclass
class UnaryExpressionNode:
    operator: "UnaryOperator"
    operand: "Node"

@dataclass
class BinaryExpressionNode:
    operator: "BinaryOperator"
    left: "Node"
    right: "Node"

@dataclass
class NumberLiteralNode:
    value: str

@dataclass
class StringLiteralNode:
    value: str

@dataclass
class FunctionLiteralNode:
    params: list["Node"]
    body: "BlockNode"

@dataclass
class NoneLiteralNode:
    pass

@dataclass 
class BoolLiteralNode:
    value: bool

@dataclass
class IdentifierNode:
    value: str

@dataclass
class IfElseBlock:
    condition: Optional["Node"]
    body: "BlockNode"

@dataclass
class IfElseExpressionNode:
    conditions: List[IfElseBlock]

@dataclass
class CallExpressionNode:
    callee: "Node"
    arguments: List["Node"]

@dataclass
class IndexExpressionNode:
    indexee: "Node"
    index: "Node"

@dataclass
class BlockNode:
    statements: List["Node"]

@dataclass
class ObjectLiteralNode:
    modifier: Optional[Literal['frozen', 'sealed']]
    entries: List["ObjectLiteralEntryNode"]

@dataclass
class ObjectLiteralEntryNode:
    is_var: bool
    name: "Node"
    value: "Node"

def pretty_print(node: "Node | IfElseBlock", indent: str, is_last: bool):
    print(indent, end="")
    if is_last:
        print("\\-", end="")
        indent += "  "
    else:
        print("|-", end="")
        indent += "| "

    match node:
        case ProgramNode():
            print("program")
            pretty_print(node.body, indent, True)

        case LetStatementNode():
            print("let-statement")
            pretty_print(node.left, indent, False)
            pretty_print(node.right, indent, True)

        case ExpressionStatementNode():
            print("expr-statement")
            pretty_print(node.expression, indent, True)

        case BinaryExpressionNode():
            print(f"binary-expression {node.operator}")
            pretty_print(node.left, indent, False)
            pretty_print(node.right, indent, True)

        case UnaryExpressionNode():
            print(f"unary-expression {node.operator}")
            pretty_print(node.operand, indent, True)

        case NumberLiteralNode():
            print(f"number '{node.value}'")

        case StringLiteralNode():
            print(f"string '{node.value}'")

        case BoolLiteralNode():
            print(f"bool '{node.value}'")

        case NoneLiteralNode():
            print(f"none")

        case IdentifierNode():
            print(f"identifier '{node.value}'")

        case IfElseBlock():
            print("if-block")
            if node.condition is not None:
                pretty_print(node.condition, indent, False)
                pretty_print(node.body, indent, True)
            else:
                pretty_print(node.body, indent, True)
                
        case IfElseExpressionNode():
            print("if-else")
            for block in node.conditions[0:-1]:
                pretty_print(block, indent, False)

        case CallExpressionNode():
            print("call")
            pretty_print(node.callee, indent, False)
            for entry in node.arguments[0:-1]:
                pretty_print(entry, indent, False)
            if len(node.arguments) > 0:
                pretty_print(node.arguments[-1], indent, True)

        case IndexExpressionNode():
            print("index")
            pretty_print(node.indexee, indent, False)
            pretty_print(node.index, indent, True)

        case BlockNode():
            print(f"block")
            for entry in node.statements[0:-1]:
                pretty_print(entry, indent, False)
            if len(node.statements) > 0:
                pretty_print(node.statements[-1], indent, True)

        case ObjectLiteralNode():
            print(f"{node.modifier if node.modifier else ''} object literal")
            for entry in node.entries[0:-1]:
                pretty_print(entry, indent, False)
            if len(node.entries) > 0:
                pretty_print(node.entries[-1], indent, True)

        case ObjectLiteralEntryNode():
            print(f"{'var' if node.is_var else ''} entry")
            pretty_print(node.name, indent, False) # type: ignore
            pretty_print(node.value, indent, True)
        
        case _:
            raise Exception(f"Not implemented on {type(node)}")

type Node = Union[
    ProgramNode,
    LetStatementNode,
    ExpressionStatementNode,
    UnaryExpressionNode,
    BinaryExpressionNode,
    NumberLiteralNode,
    StringLiteralNode,
    BoolLiteralNode,
    NoneLiteralNode,
    IdentifierNode,
    IfElseExpressionNode,
    CallExpressionNode,
    IndexExpressionNode,
    BlockNode,
    ObjectLiteralNode,
    ObjectLiteralEntryNode,
]

