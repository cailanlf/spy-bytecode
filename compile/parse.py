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

    def binary_left_associative_powers(power):
        return ((power + 1) * 2 - 1, (power + 1) * 2)
    
    def binary_right_associative_powers(power):
        return ((power + 1) * 2, (power + 1) * 2 - 1)
    
    def unary_power(power):
        return (power + 1) * 2
    
    def get_unary_precedence_prefix(self, token: Token):
        if token.type != "operator": return 0
        
        if token.value == "-" or token.value == "+":
            return self.unary_power(self.precedence_unary_minus)
        else: return 0

    def get_unary_precedence_postfix(self, token: Token):
        if token.type != "operator": return 0

        return 0
    
    def get_binary_precedence(self, token: Token):
        if token.type != "operator": return (0, 0)
        
        if token.value in ("*", "/", "%"):
            return self.binary_left_associative_powers(self.precedence_multiplicative)
        elif token.value in ("+", "-"):
            return self.binary_left_associative_powers(self.precedence_additive)
        elif token.value == ".":
            return self.binary_left_associative_powers(self.precedence_member_access)
        else:
            return (0, 0)
    #
    ## 

    def parse(self):
        statements = []

        while self.peek() is not None:
            statements.append(self.parse_statement())
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
    
    def parse_expression_power(self, min_precedence):
        prefix_precedence = self.get_unary_precedence_prefix(self.peek())
        left = None

        if prefix_precedence != None and prefix_precedence >= min_precedence:
            operator = self.expect("operator")
            operand = self.parse_expression_power(prefix_precedence)
            left = {
                "type": "unary_expression",
                "operator": operator.value,
                "operand": operand,
            }
        else:
            left = self.parse_atomic_expression()

        while True:
            postfix_precedence = self.get_unary_precedence_postfix(self.peek())
            
            if postfix_precedence == 0 and postfix_precedence < min_precedence:
                break
            
            if postfix_precedence != None and postfix_precedence >= min_precedence:
                operator = self.expect("operator")
                left = {
                    "type": "unary_expression",
                    "operator": operator.value,
                    "operand": left,
                }

        while True:
            left_precedence, right_precedence = self.get_binary_precedence(self.peek())
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

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def expect(self, type, value=None):
        token = self.peek()

        if token is None:
            raise Exception(f"Unexpected end of input, expected {type}")
        if token.type != type:
            if value == None:
                raise Exception(f"Unexpected token {token}, expected {type}")
            else:
                raise Exception(f"Unexpected token {token}, expected {type} with value {value}")
        elif value is not None and token.value != value:
            raise Exception(f"Unexpected token {token}, expected {type} with value {value}")
        
        self.pos += 1
        return token