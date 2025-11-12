from dataclasses import dataclass
from typing import Union, Literal

from lex.token import Token, Keyword_true, Keyword_false

Node = Union[
    'ProgramNode',
    'LetStatementNode',
    'ExpressionStatementNode',
    'NumberLiteralExpressionNode',
    'IdentifierExpressionNode',
    'IdentifierNode',
    'NumberLiteralNode',
    'StringLiteralNode',
    'BoolLiteralNode',
    'Expression',
    'AtomicExpression',
    'ArgumentListNode',
    'ParameterListNode',
    'BlockNode',
    'ObjectLiteralEntryNode',
    'AssignmentExpressionNode',
    'ArgumentNode',
    'ParameterNode',
]

@dataclass(frozen=True)
class ProgramNode():
    statements: list['TopLevelStatement']

TopLevelStatement = Union[
    'LetStatementNode',
    'ExpressionStatementNode',
]

Statement = Union [
    'LetStatementNode',
    'ExpressionStatementNode',
]

@dataclass(frozen=True) 
class LetStatementNode():
    name: 'IdentifierNode'
    value: 'Expression'
    mutable: bool

@dataclass(frozen=True)
class ExpressionStatementNode():
    expr: 'Expression'

Expression = Union[
    'PrefixExpressionNode',
    'PostfixExpressionNode',
    'BinaryExpressionNode',
    'AtomicExpression',
    'AssignmentExpressionNode',
    'IfElseExpressionNode',
    'LoopExpressionNode',
    'BreakExpressionNode',
    'ContinueExpressionNode',
    'CallExpressionNode',
    'IndexExpressionNode',
]

AtomicExpression = Union[
    'IdentifierExpressionNode',
    'NumberLiteralExpressionNode',
    'ObjectLiteralExpressionNode',
    'StringLiteralExpressionNode',
    'BoolLiteralExpressionNode',
    'FunctionLiteralExpressionNode',
]

@dataclass(frozen=True)
class NumberLiteralExpressionNode():
    number: 'NumberLiteralNode'

@dataclass(frozen=True)
class NumberLiteralNode():
    token: Token

    def __init__(self, token: Token):
        assert token.type == 'number'
        object.__setattr__(self, "token", token)

@dataclass(frozen=True)
class IdentifierExpressionNode():
    identifier: 'IdentifierNode'

@dataclass(frozen=True)
class IdentifierNode():
    token: Token

    def __init__(self, token: Token):
        assert token.type == 'identifier'
        object.__setattr__(self, "token", token)

@dataclass(frozen=True)
class ObjectLiteralExpressionNode():
    contents: 'list[ObjectLiteralEntryNode]'

@dataclass(frozen=True)
class ObjectLiteralEntryNode():
    name: Expression
    value: Expression
    mutable: bool

@dataclass(frozen=True)
class StringLiteralExpressionNode():
    string: 'StringLiteralNode'

@dataclass(frozen=True)
class StringLiteralNode():
    token: Token

    def __init__(self, token: Token):
        assert token.type == 'string'
        object.__setattr__(self, "token", token)

@dataclass(frozen=True)
class BoolLiteralExpressionNode():
    bool: 'BoolLiteralNode'

@dataclass(frozen=True)
class BoolLiteralNode():
    token: Token

    def __init__(self, token: Token):
        assert token.type == "keyword" and \
            (token.content == Keyword_true or token.content == Keyword_false)
        object.__setattr__(self, "token", token)

    def get_value(self):
        return True if self.token.content == Keyword_true else False 

@dataclass(frozen=True)
class BinaryExpressionNode():
    left: Expression
    right: Expression
    operator: 'BinaryOperator'

@dataclass(frozen=True)
class AssignmentExpressionNode():
    left: IdentifierExpressionNode
    value: Expression

BinaryOperator = Literal[
    'plus',
    'minus',
    'asterisk',
    'slash',
    'equalsequals',
    'bangequals',
    'greater',
    'greaterequals',
    'less',
    'lessequals',
    'and',
    'or',
]

PrefixOperator = Literal[
    'minus',
    'plus',
    'bang'
]

PostfixOperator = Literal[
    None,
]

@dataclass(frozen=True)
class PrefixExpressionNode():
    operand: Expression
    operator: PrefixOperator

@dataclass(frozen=True)
class PostfixExpressionNode():
    operand: Expression
    operator: PostfixOperator

@dataclass(frozen=True)
class BlockNode():
    statements: tuple[Statement, ...]

@dataclass(frozen=True)
class IfElseExpressionNode():
    cases: tuple[tuple[Expression | None, BlockNode]]

@dataclass(frozen=True)
class LoopExpressionNode():
    body: BlockNode

@dataclass(frozen=True)
class BreakExpressionNode():
    expr: Expression|None

@dataclass(frozen=True)
class ContinueExpressionNode():
    pass

@dataclass(frozen=True)
class CallExpressionNode():
    callee: Expression
    arglist: 'ArgumentListNode'

@dataclass(frozen=True)
class IndexExpressionNode():
    left: Expression
    index: Expression

@dataclass(frozen=True)
class ArgumentListNode():
    arguments: tuple['ArgumentNode']

@dataclass(frozen=True)
class ArgumentNode():
    expr: Expression

@dataclass(frozen=True)
class FunctionLiteralExpressionNode():
    paramlist: 'ParameterListNode'
    body: BlockNode

@dataclass(frozen=True)
class ParameterListNode():
    parameters: tuple['ParameterNode']

@dataclass(frozen=True)
class ParameterNode():
    name: IdentifierNode