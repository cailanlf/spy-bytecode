
from typing import TypedDict, Union, List, Optional
from lex import Token

# --- Node type definitions ---
class ProgramNode(TypedDict):
    type: str  # "program"
    body: List["Node"]

class LetStatementNode(TypedDict):
    type: str  # "let_statement"
    name: str
    value: "Node"

class UnaryExpressionNode(TypedDict):
    type: str  # "unary_expression"
    operator: str
    operand: "Node"

class BinaryExpressionNode(TypedDict):
    type: str  # "binary_expression"
    operator: str
    left: "Node"
    right: "Node"

class NumberLiteralNode(TypedDict):
    type: str  # "number_literal"
    value: str

class StringLiteralNode(TypedDict):
    type: str  # "string_literal"
    value: str

class IdentifierNode(TypedDict):
    type: str  # "identifier"
    value: str

class IfElseBlock(TypedDict):
    condition: Optional["Node"]
    body: List["Node"]

class IfElseExpressionNode(TypedDict):
    type: str  # "if_else_expression"
    conditions: List[IfElseBlock]

class CallExpressionNode(TypedDict):
    type: str  # "call_expression"
    callee: "Node"
    arguments: List["Node"]

class BlockNode(TypedDict):
    type: str  # "block"
    statements: List["Node"]

class ObjectLiteralNode(TypedDict):
    type: str  # "object_literal"
    modifier: Optional[str]
    entries: List["ObjectLiteralEntryNode"]

class ObjectLiteralEntryNode(TypedDict):
    type: str  # "object_literal_entry"
    is_var: bool
    name: str
    value: "Node"

Node = Union[
    ProgramNode,
    LetStatementNode,
    UnaryExpressionNode,
    BinaryExpressionNode,
    NumberLiteralNode,
    StringLiteralNode,
    IdentifierNode,
    IfElseExpressionNode,
    CallExpressionNode,
    BlockNode,
    ObjectLiteralNode,
    ObjectLiteralEntryNode,
]
# --- End Node type definitions ---

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
    precedence_comparison = 3
    precedence_member_access = 4

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
        elif token.value in ("==", "!=", "<", ">", "<=", ">="):
            return Parser.binary_left_associative_powers(Parser.precedence_comparison)
        else:
            return (0, 0)
    #
    ## 

    def parse(self) -> ProgramNode:
        statements = []

        while self.peek().type != "eof":
            statements.append(self.parse_statement())
        self.expect("eof")
        return {
            "type": "program",
            "body": statements,
        }
    
    def parse_statement(self) -> Node:
        token = self.peek()
        if token.type == "keyword" and token.value == "let":
            return self.parse_let_statement()
        else:
            return self.parse_expression()
        
    def parse_let_statement(self) -> LetStatementNode:
        self.expect("keyword", "let")
        identifier = self.expect("identifier")
        self.expect("operator", "=")
        expression = self.parse_expression()
        return { 
            "type": "let_statement", 
            "name": identifier.value,
            "value": expression, 
        }
    
    def parse_expression(self) -> Node:
        res = self.parse_expression_power(0)

        if self.peek().type == "parenthesis" and self.peek().value == "(":
            return self.parse_call_expression(callee=res)
        else: return res
        
    
    # Binary / unary disambiguation:
    # Operators that are not separated from their operand by a whitespace are 
    # treated as unary UNLESS they are between two expressions.
    # 3 +3 => 3 (+3)     invalid
    # 3+ 3 => (3+) 3     invalid
    # 3+ +3 => (3+) (+3) invalid
    #
    # By extension, unary operators must not be separated from their operand by 
    # whitespace.

    def parse_expression_power(self, min_precedence) -> Node:
        prefix_precedence = Parser.get_unary_precedence_prefix(self.peek())

        if prefix_precedence != 0 and prefix_precedence >= min_precedence:
            operator = self.expect("operator")
            if self.peek().whitespace_before:
                raise self.error(f"while parsing prefix unary operator: unexpected whitespace before {self.peek()}, expected unary operator or atomic expression")
            operand = self.parse_expression_power(prefix_precedence)
            left = {
                "type": "unary_expression",
                "operator": operator.value,
                "operand": operand,
            }
        else:
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
    
    def parse_atomic_expression(self) -> Node:
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
                or self.peek().type == "parenthesis" and self.peek().value == "{":
            return self.parse_object_literal()
        elif self.peek().type == "identifier":
            value = self.expect("identifier")
            return {
                "type": "identifier",
                "value": value.value,
            }
        elif self.peek().type == "keyword" and self.peek().value == "if":
            return self.parse_if_else_expression()
        else:
            raise self.error(f"while parsing atomic: unexpected token {self.peek()}, expected atomic expression")
    
    def parse_if_else_expression(self) -> IfElseExpressionNode:
        """
            if_else_expression =
                | "if" expression ":" statement* ("elif" expression ":" statement*)* ("end" | ("else" expression ":" statement* "end"))
        """

        
        self.expect("keyword", "if")
        condition = self.parse_expression()
        self.expect("punctuation", ":")

        blocks = []
        statements = []

        while not (self.peek().type == "keyword" and self.peek().value in {"elif", "else", "end"}):
            statements.append(self.parse_statement())

        blocks.append({
            "condition": condition,
            "body": statements,
        })

        while self.peek().type == "keyword" and self.peek().value == "elif":
            self.expect("keyword", "elif")
            condition = self.parse_expression()
            self.expect("punctuation", ":")
            statements = []

            while not (self.peek().type == "keyword" and self.peek().value in {"elif", "else", "end"}):
                statements.append(self.parse_statement())
            
            blocks.append({
                "condition": condition,
                "body": statements,
            })

        if self.peek().type == "keyword" and self.peek().value == "else":
            self.expect("keyword", "else")
            self.expect("punctuation", ":")
            statements = []

            while not (self.peek().type == "keyword" and self.peek().value == "end"):
                statements.append(self.parse_statement())
            
            blocks.append({
                "condition": None,
                "body": statements,
            })

        self.expect("keyword", "end")

        return {
            "type": "if_else_expression",
            "conditions": blocks,
        }

       
    
    def parse_call_expression(self, callee=None) -> CallExpressionNode:
        """
            call_expression =
                | expression "(" ((expression comma)* expression)? ")"
        """

        if callee is None:
            callee = self.parse_expression()
        self.expect("parenthesis", "(")

        arguments = []
        if not (self.peek().type == "parenthesis" and self.peek().value == ")"):
            while True:
                arguments.append(self.parse_expression())
                if self.peek().type == "comma":
                    self.expect("comma")
                else:
                    break

        self.expect("parenthesis", ")")

        return {
            "type": "call_expression",
            "callee": callee,
            "arguments": arguments,
        }

    def parse_block(self) -> BlockNode:
        """
            block = 
            | ":" statement* "end"
        """
        self.expect("punctuation", ":")
        statements = []

        while not (self.peek().type == "keyword" and self.peek().value == "end"):
            statements.append(self.parse_statement())
        
        self.expect("keyword", "end")

        return {
            "type": "block",
            "statements": statements,
        }

    def parse_object_literal(self) -> ObjectLiteralNode:
        """
            object_literal = 
                | ("frozen" | "sealed")? "{" (object_literal_entry)* "}"
            ;
        """
        modifier = None

        if self.peek().type == "keyword" and self.peek().value in {"frozen", "sealed"}:
            match self.peek().value:
                case "frozen":
                    modifier = "frozen"
                case "sealed":
                    modifier = "sealed"
                case _:
                    raise self.error(f"Unexpected modifier {self.peek().value}, expected 'frozen' or 'sealed'")
            self.expect("keyword")
        
        self.expect("parenthesis", "{")

        entries = []

        while not (self.peek().type == "parenthesis" and self.peek().value == "}"):
            entries.append(self.parse_object_literal_entry())

        self.expect("parenthesis", "}")

        return {
            "type": "object_literal",
            "modifier": modifier,
            "entries": entries,
        }
    
    def parse_object_literal_entry(self) -> ObjectLiteralEntryNode:
        """
            object_literal_entry = 
                | "var"? identifier "=" expression
                ;
        """
        is_var = False

        if self.peek().type == "keyword" and self.peek().value == "var":
            self.expect("keyword", "var")
            is_var = True
        
        name = self.expect("identifier")
        self.expect("operator", "=")
        value = self.parse_expression()

        if self.peek().type == "comma":
            self.expect("comma")

        return {
            "type": "object_literal_entry",
            "is_var": is_var,
            "name": name.value,
            "value": value,
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