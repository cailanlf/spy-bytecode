from lex.token import Token, TokenType, Keywords

class Lexer():
    tokens: list[Token]
    pos: int
    whitespace_before: bool

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.tokens = []
    
    def lex(self) -> list[Token]:
        self.pos = 0
        self.tokens = []
        self.whitespace_before = False

        while (next := self.peek()) is not None:
            match next:
                case '(':
                    self.emit('lparen', 1)
                case ')':
                    self.emit('rparen', 1)
                case '{':
                    self.emit('lcurly', 1)
                case '}':
                    self.emit('rcurly', 1)
                case '[':
                    self.emit('lbracket', 1)
                case ']':
                    self.emit('rbracket', 1)
                case ',':
                    self.emit('comma', 1)
                case '.':
                    self.emit('period', 1)
                case '+':
                    self.emit('plus', 1)
                case '-':
                    self.emit('minus', 1)
                case '/':
                    self.emit('slash', 1)
                case '|':
                    self.emit('pipe', 1)
                case '*':
                    self.emit('asterisk', 1)
                case '>':
                    if self.peek(1) == '=':
                        self.emit('greaterequals', 2)
                    else:
                        self.emit('greater', 1)
                case '<':
                    if self.peek(1) == '=':
                        self.emit('lessequals', 2)
                    else:
                        self.emit('less', 1)
                case '!':
                    if self.peek(1) == '!':
                        self.emit('bangequals', 2)
                    else:
                        self.emit('bang', 1)
                case '=':
                    if self.peek(1) == '=':
                        self.emit('equalsequals', 2)
                    self.emit('equals', 1)
                case ':':
                    self.emit('colon', 1)
                case _:
                    if next.isdigit():
                        self.lex_number()
                    elif next.isalpha() or next == '_':
                        self.lex_identifier()
                    elif next == '\t' or next == '\r' or next == ' ' or next == '\n':
                        self.whitespace_before = True
                        self.consume()
                    elif next == "'" or next == '"':
                        self.lex_string()
                    else:
                        raise Exception("lexer: unrecognized character")
        
        self.emit('eof', 0)
        return self.tokens

    def lex_number(self):
        offset = 0

        while (peeked := self.peek(offset)) is not None and peeked.isdigit():
            offset += 1

        if offset == 0:
            raise Exception("lex: tried to emit number token of length 0")
        
        self.emit('number', offset)

    def lex_string(self):
        quote_type = None
        if self.peek() == "'":
            quote_type = "'"
        elif self.peek() == '"':
            quote_type = '"'
        else:
            raise Exception(f"lex: invalid string delimiter {self.peek}")

        offset = 1

        last_was_backslash = False
        while (peeked := self.peek(offset)) is not None:
            if not last_was_backslash and peeked == quote_type:
                break

            if peeked == "\\" and not last_was_backslash:
                last_was_backslash = True

            offset += 1
        
        if self.peek(offset) is None:
            raise Exception("unterminated string literal")
        
        offset += 1
        return self.emit('string', offset)

    def lex_identifier(self):
        offset = 0

        while ((peeked := self.peek(offset)) is not None) and \
                (peeked.isalpha() or peeked == "_" or (offset > 0 and peeked.isdigit())):
            offset += 1

        if offset == 0:
            raise Exception("lex: tried to emit identifier token of length 0")

        if self.source[self.pos : (self.pos + offset)] in Keywords:
            self.emit('keyword', offset)
        else:
            self.emit('identifier', offset)

    def peek(self, offset = 0):
        if self.pos + offset < len(self.source):
            return self.source[self.pos + offset]
        else:
            return None
        
    def emit(self, type: TokenType, length: int):
       self.emit_custom_value(type, length, self.source[self.pos : (self.pos + length)])
        
    def emit_custom_value(self, type: TokenType, length: int, value: str):
        if len(self.tokens) > 0:
            self.tokens[-1].whitespace_after = self.whitespace_before
        
        self.tokens.append(Token(
            type=type,
            content=value,
            position=(self.pos, self.pos + length),
            whitespace_before=self.whitespace_before,
            whitespace_after=False
        ))

        self.pos += length
        self.whitespace_before = False
        
    def consume(self):
        if self.pos < len(self.source):
            consumed = self.source[self.pos]
            self.pos += 1
            return consumed
        else:
            raise Exception("lexer: consumed beyond end of input")