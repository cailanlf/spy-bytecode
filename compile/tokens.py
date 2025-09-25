from dataclasses import dataclass
from typing import Literal, Union

@dataclass
class BaseToken():
    whitespace_before: bool
    whitespace_after: bool
    position: tuple[int, int]

@dataclass
class NumberToken(BaseToken):
    value: str

@dataclass
class StringToken(BaseToken):
    value: str

@dataclass
class IdentifierToken(BaseToken):
    value: str

@dataclass
class KeywordToken(BaseToken):
    value: Literal["let", "var", "end", "freeze", "seal", "frozen", "sealed", "if", "else", "True", "False", "None", "func"]

BinaryOperator = Literal["+", "-", "*", "/", "%", "=", "==", "!=", "<", "<=", ">", ">=", "."]
PrefixUnaryOperator = Literal["-", "+", "!"]
PostfixUnaryOperator = Literal["["]
UnaryOperator = Union[PrefixUnaryOperator | PostfixUnaryOperator]

@dataclass
class OperatorToken(BaseToken):
    value: Union[BinaryOperator, UnaryOperator]

type Parenthesis = Literal["(", ")", "{", "}", "[", "]"]

@dataclass
class ParenthesisToken(BaseToken):
    value: Parenthesis

@dataclass
class PunctuationToken(BaseToken):
    value: Literal[",", ":"]

@dataclass
class EOFToken(BaseToken):
    pass

type Token = Union[NumberToken, StringToken, IdentifierToken, KeywordToken, OperatorToken, ParenthesisToken, PunctuationToken, EOFToken]