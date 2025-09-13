from lex import Token

class Parser():
    tokens: list[Token]
    pos: int = 0

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    ##
    # Utilities for pratt parsing
    precedence_unary_minus = 0
    precedence_multiplicative = 1
    precedence_additive = 2
    precedence_member_access = 3

    @staticmethod
    def binary_left_associative_powers(power):
        return ((power + 1) * 2 - 1, (power + 1) * 2)
    
    @staticmethod
    def binary_right_associative_powers(power):
        return ((power + 1) * 2, (power + 1) * 2 - 1)
    
    @staticmethod
    def unary_power(power):
        return (power + 1) * 2
    
    @staticmethod
    def get_unary_precedence_prefix(token: Token):
        if token.type != "operator": return 0
        
        if token.value == "-" or token.value == "+":
            return Parser.unary_power(Parser.precedence_unary_minus)
        else: return 0

    @staticmethod
    def get_unary_precedence_postfix(token: Token):
        if token.type != "operator": return 0

        return 0
    
    def get_binary_precedence(token: Token):
        if token.type != "operator": return (0, 0)
        
        if token.value in ("*", "/", "%"):
            return Parser.binary_left_associative_powers(Parser.precedence_multiplicative)
        elif token.value in ("+", "-"):
            return Parser.binary_left_associative_powers(Parser.precedence_additive)
        elif token.value == ".":
            return Parser.binary_left_associative_powers(Parser.precedence_member_access)
        else:
            return (0, 0)
    #
    ## 

    def parse(self):
        statements = []

        while self.peek().type != "eof":
            statements.append(self.parse_statement())
        self.expect("eof")
        return statements
    
    def parse_statement(self):
        token = self.peek()
        if token.type == "keyword" and token.value == "let":
            return self.parse_let_statement()
        else:
            return self.parse_expression()
        
    def parse_let_statement(self):
        self.expect("keyword", "let")
        identifier = self.expect("identifier")
        self.expect("operator", "=")
        expression = self.parse_expression()
        return { 
            "type": "let_statement", 
            "name": identifier.value,
            "value": expression, 
        }
    
    def parse_expression(self):
        return self.parse_expression_power(0)
    
    # Binary / unary disambiguation:
    # Operators that are not separated from their operand by a whitespace are 
    # treated as unary UNLESS they are between two expressions.
    # 3 +3 => 3 (+3)     invalid
    # 3+ 3 => (3+) 3     invalid
    # 3+ +3 => (3+) (+3) invalid
    #
    # By extension, unary operators must not be separated from their operand by 
    # whitespace.

    def parse_expression_power(self, min_precedence):
        prefix_precedence = Parser.get_unary_precedence_prefix(self.peek())

        if prefix_precedence != 0 and prefix_precedence >= min_precedence:
            operator = self.expect("operator")
            operand = self.parse_expression_power(prefix_precedence)
            left = {
                "type": "unary_expression",
                "operator": operator.value,
                "operand": operand,
            }
        else:
            if self.peek().whitespace_before:
                raise self.error(f"while parsing prefix unary operator: unexpected whitespace before {self.peek()}, expected unary operator or atomic expression")
            left = self.parse_atomic_expression()

        while True:
            postfix_precedence = Parser.get_unary_precedence_postfix(self.peek())
            
            if postfix_precedence == 0 or postfix_precedence < min_precedence:
                break

            operator = self.expect("operator")
            operand = left
            left = {
                "type": "unary_expression",
                "operator": operator.value,
                "operand": operand,
            }

        while True:
            left_precedence, right_precedence = Parser.get_binary_precedence(self.peek())

            if left_precedence == 0 or left_precedence < min_precedence:
                break

            operator = self.expect("operator")
            right = self.parse_expression_power(right_precedence)
            left = {
                "type": "binary_expression",
                "operator": operator.value,
                "left": left,
                "right": right,
            }

        return left
    
    def parse_atomic_expression(self):
        """
            atomic_expression = 
                | number_literal
                | string_literal
                | object_literal
                ;
        """
        if self.peek().type == "number":
            value = self.expect("number")
            return {
                "type": "number_literal",
                "value": value.value,
            }
        elif self.peek().type == "string":
            value = self.expect("string")
            return {
                "type": "string_literal",
                "value": value.value,
            }
        elif self.peek().type == "keyword" and self.peek().value in ("frozen", "sealed") \
                or self.peek().type == "punctuation" and self.peek().value == "{":
            return self.parse_object_literal()
        else:
            raise self.error(f"while parsing atomic: unexpected token {self.peek()}, expected atomic expression")

    def parse_object_literal(self):
        """
            object_literal = 
                | ("frozen" | "sealed")? "{" (object_literal_entry)* "}"
            ;
        """
        modifier = None

        if self.peek().type == "keyword" and self.peek().value in ("frozen", "sealed"):
            modifier = self.expect("keyword")
        
        self.expect("punctuation", "{")

        entries = []

        while not (self.peek().type == "punctuation" and self.peek().value == "}"):
            entries.append(self.parse_object_literal_entry())

        self.expect("punctuation", "}")

        return {
            "type": "object_literal",
            "modifier": modifier,
            "entries": entries,
        }

    def peek(self, offset=0):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return self.tokens[-1]
    
    def expect(self, type, value=None):
        token = self.peek()

        if token is None:
            raise self.error(f"Unexpected end of input, expected {type}")
        if token.type != type:
            if value == None:
                raise self.error(f"Unexpected token {token}, expected {type}")
            else:
                raise self.error(f"Unexpected token {token}, expected {type} with value {value}")
        elif value is not None and token.value != value:
            raise self.error(f"Unexpected token {token}, expected {type} with value {value}")
        
        self.pos += 1
        return token
    
    def error(self, message: str):
        return Exception(f"Error at index {self.peek().position}: {message}")