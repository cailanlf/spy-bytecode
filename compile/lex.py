from tokens import *

from typing import Literal, Union, TypeVar
from dataclasses import dataclass

class Lexer():
    input: str
    pos: int = 0
    tokens: list[Token] = []
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
            elif next in ['+', '-', '*', '/', '%', '.']:
                self.emit(OperatorToken, 1)
            elif next in ['=', '!', '<', '>']:
                if self.pos + 1 < len(self.input) and self.input[self.pos + 1] == '=':
                    self.emit(OperatorToken, 2)
                else:
                    self.emit(OperatorToken, 1)
            elif next in ['(', ')', '{', '}', '[', ']']:
                self.emit(ParenthesisToken, 1)
            elif next == ',':
                self.emit(PunctuationToken, 1)
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
                self.emit(PunctuationToken, 1)
            elif next.isdigit():
                self.lex_number()
            else: 
                raise Exception(f"Unexpected character: {next}")

        self.tokens.append(EOFToken(whitespace_before=False, whitespace_after=False, position=(self.pos, self.pos)))
        return self.tokens 
    
    def lex_number(self):
        index = self.pos
        while index < len(self.input) and self.input[index].isdigit():
            index += 1
        self.emit(NumberToken, index - self.pos)

    def lex_identifier(self):
        index = self.pos
        while index < len(self.input) and (self.input[index].isalnum() or self.input[index] == '_'):
            index += 1
        value = self.input[self.pos:index]

        if value in {"let", "var", "end", "freeze", "seal", "frozen", "sealed", "if", "else", 'True', 'False', 'None'}:
            self.emit(KeywordToken, index - self.pos)
        else:
            self.emit(IdentifierToken, index - self.pos)

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
        self.emit_custom_value(StringToken, index + 1 - self.pos, value=self.input[self.pos + 1 : index]) # + 1 to include closing quote

    def emit_custom_value[T](self, typ: type[Token], length: int, value: str):
        if len(self.tokens) > 0:
            self.tokens[-1].whitespace_after = self.whitespace_before
        token = typ(value=value, # type: ignore
                    whitespace_before=self.whitespace_before, 
                    whitespace_after=False, 
                    position=(self.pos, self.pos + length))
        self.tokens.append(token)
        self.pos += length
        self.whitespace_before = False
        
    def emit[T](self, typ: type[Token], length: int):
        self.emit_custom_value(typ, length, self.input[self.pos:self.pos+length])