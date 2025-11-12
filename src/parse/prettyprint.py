from typing import Collection, Generator, TypeVar

from parse.parsenode import *
from parse.idintern import IdIntern

_c = '\x1b[1;34m'
_y = '\x1b[33m'
_o = '\x1b[0m'
T = TypeVar('T')

def __with_last(iterable: Collection[T]) -> Generator[tuple[T, bool], None, None]:
    for i, elem in enumerate(iterable):
        yield (elem, i >= len(iterable) - 1)

def pretty_print(node: Node, indent: str, is_last: bool, intern: IdIntern):
    print(indent, end="")
    print("╰── " if is_last else "├── ", end="")
    indent = indent + ("    " if is_last else "│   ")
    print(f"({intern.intern_id(id(node))}) ", end="")

    match node:
        case ProgramNode():
            print(f"{_c}program:{_o}")
            for elem, is_last in __with_last(node.statements):
                pretty_print(elem, indent, is_last, intern)

        case LetStatementNode():
            print(f"{_c}let-statement:{_o}")
            pretty_print(node.name, indent, False, intern)
            pretty_print(node.value, indent, True, intern)
        
        case NumberLiteralNode():
            print(f"{_c}number-literal:{_o} {_y}{node.token.content}{_o}")

        case IdentifierNode():
            print(f"{_c}identifier:{_o} {_y}{node.token.content}{_o}")

        case StringLiteralNode():
            print(f"{_c}string-literal:{_o} {_y}{node.token.content}{_o}")

        case IdentifierExpressionNode():
            print(f"{_c}identifier-expression{_o}:")
            pretty_print(node.identifier, indent, True, intern)

        case NumberLiteralExpressionNode():
            print(f"{_c}number-literal-expression:{_o}")
            pretty_print(node.number, indent, True, intern)

        case StringLiteralExpressionNode():
            print(f"{_c}string-literal-expression:{_o}")
            pretty_print(node.string, indent, True, intern)

        case ObjectLiteralExpressionNode():
            print(f"{_c}object-literal-expression:{_o}")
            for (elem, is_last) in __with_last(node.contents):
                pretty_print(elem, indent, is_last, intern)
            
        case ObjectLiteralEntryNode():
            print(f"{_c}object-literal-entry:{_o}")
            pretty_print(node.name, indent, False, intern)
            pretty_print(node.value, indent, True, intern)

        case BoolLiteralExpressionNode():
            print(f"{_c}bool-literal-expression:{_o}")
            pretty_print(node.bool, indent, True, intern)
        
        case BoolLiteralNode():
            print(f"{_c}bool-literal:{_o} {_y}{node.token.content}{_o}")

        case FunctionLiteralExpressionNode():
            print(f"{_c}function-literal-expression{_o}:")
            pretty_print(node.paramlist, indent, False, intern)
            pretty_print(node.body, indent, True, intern)

        case ParameterListNode():
            print(f"{_c}parameter-list{_o}:")
            for param, is_last in __with_last(node.parameters):
                pretty_print(param, indent, is_last, intern)

        case ParameterNode():
            print(f"{_c}parameter:{_o}")
            pretty_print(node.name, indent, True, intern)

        case PrefixExpressionNode():
            print(f"{_c}prefix-expression:{_o} {_y}{node.operator}{_o}")
            pretty_print(node.operand, indent, True, intern)

        case PostfixExpressionNode():
            print(f"{_c}postfix-expression:{_o} {_y}{node.operator}{_o}")
            pretty_print(node.operand, indent, True, intern)

        case BinaryExpressionNode():
            print(f"{_c}binary-expression:{_o} {_y}{node.operator}{_o}")
            pretty_print(node.left, indent, False, intern)
            pretty_print(node.right, indent, True, intern)

        case AssignmentExpressionNode():
            print(f"{_c}assignment-expression:{_o}")
            pretty_print(node.left, indent, False, intern)
            pretty_print(node.value, indent, True, intern)

        case IfElseExpressionNode():
            print(f"{_c}if-else-expression:{_o}")
            for (cond, block), is_last in __with_last(node.cases):
                if (cond is not None):
                    pretty_print(cond, indent, False, intern)
                pretty_print(block, indent, is_last, intern)
        
        case BlockNode():
            print(f"{_c}block:{_o}")
            for statement, is_last in __with_last(node.statements):
                pretty_print(statement, indent, is_last, intern)

        case ExpressionStatementNode():
            print(f"{_c}expression-statement:{_o}")
            pretty_print(node.expr, indent, True, intern)

        case CallExpressionNode():
            print(f"{_c}call-expression:{_o}")
            pretty_print(node.callee, indent, False, intern)
            pretty_print(node.arglist, indent, True, intern)

        case IndexExpressionNode():
            print(f"{_c}index-expression:{_o}")
            pretty_print(node.left, indent, False, intern)
            pretty_print(node.index, indent, True, intern)

        case ArgumentListNode():
            print(f"{_c}argument-list:{_o}")
            for arg, is_last in __with_last(node.arguments):
                pretty_print(arg, indent, is_last, intern)

        case ArgumentNode():
            print(f"{_c}argument:{_o}")
            pretty_print(node.expr, indent, True, intern)

        case _:
            print(f"Not implemented for {type(node)}")