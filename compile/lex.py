from typing import Literal, NamedTuple

TokenType = Literal[
    'number',
    'string',
    'identifier',
    'keyword',
    'operator',
    'parenthesis',
    'comma',
]

class Token(NamedTuple):
    type: TokenType
    value: str
    whitespace_before: bool

class Lexer():
    input: str
    pos: int = 0
    tokens: list[tuple[TokenType, str, bool]] = []
    whitespace_before: bool = False

    def __init__(self, input: str):
        self.input = input

    def lex(self):
        while self.pos < len(self.input):
            next = self.input[self.pos]
            if next == ' ' or next == '\n' or next == '\t' or next == '\r':
                self.whitespace_before = True
                self.pos += 1
                continue
            elif next in ['+', '-', '*', '/', '=', '.']:
                self.emit('operator', 1)
            elif next in ['(', ')', '{', '}', '[', ']']:
                self.emit('parenthesis', 1)
            elif next == "#":
                while self.pos < len(self.input) and self.input[self.pos] != '\n':
                    self.pos += 1
                self.whitespace_before = True
                continue
            elif next.isalpha() or next == '_':
                self.lex_identifier()
            elif next == '"' or next == "'":
                self.lex_string()
            elif next == ':':
                self.emit('keyword', 1)
            elif next.isdigit():
                self.lex_number()
            else: 
                raise Exception(f"Unexpected character: {next}")

        return self.tokens 
    
    def lex_number(self):
        index = self.pos
        while index < len(self.input) and self.input[index].isdigit():
            index += 1
        self.emit('number', index - self.pos)

    def lex_identifier(self):
        index = self.pos
        while index < len(self.input) and (self.input[index].isalnum() or self.input[index] == '_'):
            index += 1
        value = self.input[self.pos:index]

        if value in ["let", "var", "end", "freeze", "seal"]:
            self.emit('keyword', index - self.pos)
        else:
            self.emit('identifier', index - self.pos)

    def lex_string(self):
        index = self.pos + 1 # + 1 to skip opening quote
        quote_type = self.input[self.pos]
        if quote_type not in ['"', "'"]:
            raise Exception("Unrecognized string delimiter")
        last_was_backslash = False
        while index < len(self.input):
            if not last_was_backslash and self.input[index] == quote_type:
                break

            last_was_backslash = False
            
            if self.input[index] == '\\':
                last_was_backslash = True

            index += 1

        if index >= len(self.input):
            raise Exception("Unterminated string literal")
        self.emit('string', index + 1 - self.pos) # + 1 to include closing quote
    
    def emit(self, type: TokenType, length: int):
        token = Token(type, self.input[self.pos:self.pos+length], self.whitespace_before)
        self.tokens.append(token)
        self.pos += length
        self.whitespace_before = False