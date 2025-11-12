from dataclasses import dataclass
from typing import Literal

# unsafe_hash: we use nodes which contain tokens as members
# later on, and we can't freeze them now since we need to
# update whitespace in the lexer.
@dataclass(unsafe_hash=True)
class Token:
    type: 'TokenType'
    content: str
    position: tuple[int, int]
    whitespace_before: bool
    whitespace_after: bool

Keyword_let = 'let'
Keyword_var = 'var'
Keyword_end = 'end'
Keyword_elif = 'elif'
Keyword_else = 'else'
Keyword_if = 'if'
Keyword_loop = 'loop'
Keyword_break = 'break'
Keyword_with = 'with'
Keyword_continue = 'continue'
Keyword_fn = 'fn'
Keyword_const = 'const'
Keyword_true = 'true'
Keyword_false = 'false'
Keyword_and = 'and'
Keyword_or = 'or'

Keywords = {
    Keyword_let,
    Keyword_var,
    Keyword_if,
    Keyword_elif,
    Keyword_else,
    Keyword_end,
    Keyword_loop,
    Keyword_break,
    Keyword_with,
    Keyword_continue,
    Keyword_fn,
    Keyword_const,
    Keyword_true,
    Keyword_false,
    Keyword_and,
    Keyword_or,
}

TokenType = Literal[
    'number',
    'identifier',
    'keyword',
    'string',
    'lparen', 
    'rparen',
    'lbracket',
    'rbracket',
    'lcurly',
    'rcurly',
    'plus',
    'minus',
    'asterisk',
    'slash',
    'greater',
    'greaterequals',
    'less',
    'lessequals',
    'bang',
    'bangequals',
    'equalsequals',
    'pipe',
    'comma',
    'period',
    'colon',
    'equals',
    'eof',
]