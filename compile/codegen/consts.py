from typing import Union, Literal
from dataclasses import dataclass

type Const = \
    IntegerConst | StringConst | BoolConst | NoneConst

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