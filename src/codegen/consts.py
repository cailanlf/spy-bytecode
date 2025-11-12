from typing import Union, Literal, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from codegen.block import Block
    
type Const = \
    IntegerConst | StringConst | BoolConst | NoneConst | FunctionLiteralConst

@dataclass
class IntegerConst:
    value: str

@dataclass
class StringConst:
    value: str

@dataclass
class BoolConst:
    value: Literal[0, 1]

@dataclass
class NoneConst:
    pass

@dataclass
class FunctionLiteralConst:
    block: 'Block'