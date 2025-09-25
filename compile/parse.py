from tokens import *
from parsenodes import *

from typing import TypeVar, Generic, Sequence, get_args, cast
from tokens import PrefixUnaryOperator

class Parser():
    tokens: Sequence[BaseToken]
    pos: int = 0

    def __init__(self, tokens: Sequence[BaseToken]):
        self.tokens = tokens

    ##
    # Utilities for pratt parsing
    precedence_assignment = 0
    precedence_additive = 1
    precedence_multiplicative = 2
    precedence_unary_minus = 3
    precedence_comparison = 4
    precedence_member_access = 5

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
    def get_unary_precedence_prefix(token: BaseToken):
        if not isinstance(token, OperatorToken): return 0
        
        if token.value == "-" or token.value == "+":
            return Parser.unary_power(Parser.precedence_unary_minus)
        else: return 0

    @staticmethod
    def get_unary_precedence_postfix(token: BaseToken):
        if type(token) is ParenthesisToken and token.value in ("["):
            return Parser.unary_power(Parser.precedence_member_access)

        return 0
    
    @staticmethod
    def get_binary_precedence(token: BaseToken):
        if not isinstance(token, OperatorToken): return (0, 0)
        
        if token.value in ("*", "/", "%"):
            return Parser.binary_left_associative_powers(Parser.precedence_multiplicative)
        elif token.value in ("+", "-"):
            return Parser.binary_left_associative_powers(Parser.precedence_additive)
        elif token.value == ".":
            return Parser.binary_left_associative_powers(Parser.precedence_member_access)
        elif token.value in ("==", "!=", "<", ">", "<=", ">="):
            return Parser.binary_left_associative_powers(Parser.precedence_comparison)
        elif token.value in ("="):
            return Parser.binary_left_associative_powers(Parser.precedence_assignment)
        else:
            return (0, 0)
    #
    ## 

    def parse(self) -> ProgramNode:
        statements = []

        while not self.peek_is(EOFToken):
            statements.append(self.parse_statement())
        self.expect(EOFToken)
        return ProgramNode(body=BlockNode(statements))
    
    def parse_statement(self) -> Node:
        if self.peek_is(KeywordToken, "let"):
            return self.parse_let_statement()
        else:
            return self.parse_expression_statement()
        
    def parse_expression_statement(self) -> ExpressionStatementNode:
        return ExpressionStatementNode(self.parse_expression())
        
    def parse_let_statement(self) -> LetStatementNode:
        self.expect(KeywordToken, "let")
        left = self.parse_expression()
        self.expect(OperatorToken, "=")
        expression = self.parse_expression()
        return LetStatementNode(left=left, right=expression)
    
    def parse_expression(self) -> Node:
        res = self.parse_expression_power(0)

        if self.peek_is(ParenthesisToken, "("): 
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
            operator = self.expect(OperatorToken)
            if self.peek().whitespace_before:
                raise self.error(f"while parsing prefix unary operator: unexpected whitespace before {self.peek()}, expected unary operator or atomic expression")
            if operator.value not in get_args(PrefixUnaryOperator):
                raise self.error(f"Invalid unary prefix operator '{operator.value}'")
            operand = self.parse_expression_power(prefix_precedence)
            value = cast(UnaryOperator, operator.value)

            left = UnaryExpressionNode(operator=value, operand=operand)
        else:
            left = self.parse_atomic_expression()

        while True:
            postfix_precedence = Parser.get_unary_precedence_postfix(self.peek())
            
            if postfix_precedence == 0 or postfix_precedence < min_precedence:
                break

            operator = self.consume()
            operand = left

            if type(operator) is not ParenthesisToken and type(operator) is not OperatorToken:
                raise self.error("Invalid postfix operator type")

            if operator.value not in get_args(PostfixUnaryOperator):
                raise self.error(f"Invalid unary postfix operator '{operator.value}'")
            
            if operator.value == "[":
                operand = self.parse_expression()
                self.expect(ParenthesisToken, ']')
                left = IndexExpressionNode(left, operand)
            else:
                operand = self.parse_expression_power(prefix_precedence)
                value = cast(UnaryOperator, operator.value)
                left = UnaryExpressionNode(operator=value, operand=operand)

        while True:
            left_precedence, right_precedence = Parser.get_binary_precedence(self.peek())

            if left_precedence == 0 or left_precedence < min_precedence:
                break

            operator = self.expect(OperatorToken)
            print(get_args(BinaryOperator))
            if operator.value not in get_args(BinaryOperator):
                raise Exception(f"Invalid binary operator '{operator.value}'")
            
            value = cast(BinaryOperator, operator.value)
            right = self.parse_expression_power(right_precedence)
            if value == ".":
                if type(right) is not IdentifierNode:
                    raise self.error("Right side of dot expression must be identifier")
                else:
                    left = IndexExpressionNode(left, StringLiteralNode(right.value))
            else:
                left = BinaryExpressionNode(operator=value, left=left, right=right)

        return left
    
    def parse_atomic_expression(self) -> Node:
        """
            atomic_expression = 
                | number_literal
                | string_literal
                | object_literal
                | identifier
                ;
        """
        if self.peek_is(NumberToken):
            value = self.expect(NumberToken)
            return NumberLiteralNode(value=value.value)
        
        elif self.peek_is(StringToken):
            value = self.expect(StringToken)
            return StringLiteralNode(value=value.value)
        
        elif self.peek_is(KeywordToken, "sealed") or self.peek_is(KeywordToken, "frozen") \
                or self.peek_is(ParenthesisToken, "{"):
            return self.parse_object_literal()
        
        elif self.peek_is(KeywordToken, "True") or self.peek_is(KeywordToken, "False"):
            value = self.expect(KeywordToken)
            if value.value == "True":
                return BoolLiteralNode(True)
            else:
                return BoolLiteralNode(False)
            
        elif self.peek_is(KeywordToken, "None"):
            value = self.expect(KeywordToken)
            return NoneLiteralNode()
        
        elif self.peek_is(IdentifierToken):
            value = self.expect(IdentifierToken)
            return IdentifierNode(value=value.value)
        
        elif self.peek_is(ParenthesisToken, "("):
            value = self.expect(ParenthesisToken)
            expr = self.parse_expression()
            self.expect(ParenthesisToken, ")")
            return expr

        elif self.peek_is(KeywordToken, "if"):
            return self.parse_if_else_expression()
        else:
            raise self.error(f"while parsing atomic: unexpected token {self.peek()}, expected atomic expression")
    
    def parse_if_else_expression(self) -> IfElseExpressionNode:
        """
            if_else_expression =
                | "if" expression ":" statement* ("elif" expression ":" statement*)* ("end" | ("else" expression ":" statement* "end"))
        """
        
        self.expect(KeywordToken, "if")
        condition = self.parse_expression()
        self.expect(PunctuationToken, ":")

        blocks = []
        statements = []

        while not self.peek_is(KeywordToken, "elif") or self.peek_is(KeywordToken, "else") \
                or self.peek_is(KeywordToken, "end"):
            statements.append(self.parse_statement())

        blocks.append({
            "condition": condition,
            "body": statements,
        })

        while self.peek_is(KeywordToken, "elif"):
            self.expect(KeywordToken, "elif")
            condition = self.parse_expression()
            self.expect(PunctuationToken, ":")
            statements = []

            while not self.peek_is(KeywordToken, "elif") or self.peek_is(KeywordToken, "else") \
                    or self.peek_is(KeywordToken, "end"):
                statements.append(self.parse_statement())
            
            blocks.append({
                "condition": condition,
                "body": BlockNode(statements),
            })

        if self.peek_is(KeywordToken, "else"):
            self.expect(KeywordToken, "else")
            self.expect(PunctuationToken, ":")
            statements = []

            while not self.peek_is(KeywordToken, "end"):
                statements.append(self.parse_statement())
            
            blocks.append({
                "condition": None,
                "body": statements,
            })

        self.expect(KeywordToken, "end")

        return IfElseExpressionNode(conditions=[IfElseBlock(condition=block["condition"], body=block["body"]) for block in blocks])
    
    def parse_call_expression(self, callee=None) -> CallExpressionNode:
        """
            call_expression =
                | expression "(" ((expression comma)* expression)? ")"
        """

        if callee is None:
            callee = self.parse_expression()
        self.expect(ParenthesisToken, "(")

        arguments = []
        if not self.peek_is(ParenthesisToken, ")"):
            while True:
                arguments.append(self.parse_expression())
                if self.peek_is(PunctuationToken, ","):
                    self.expect(PunctuationToken, ",")
                else:
                    break

        self.expect(ParenthesisToken, ")")

        return CallExpressionNode(callee=callee, arguments=arguments)
    
    def parse_index_expression(self, indexee=None) -> IndexExpressionNode:
        """
            index_expression =
                | expression "[" expression "]"
        """

        if indexee is None:
            indexee = self.parse_expression()
        self.expect(ParenthesisToken, "[")

        index = self.parse_expression()

        self.expect(ParenthesisToken, "]")

        return IndexExpressionNode(indexee=indexee, index=index)

    def parse_block(self) -> BlockNode:
        """
            block = 
            | ":" statement* "end"
        """
        self.expect(PunctuationToken, ":")
        statements = []

        while not self.peek_is(KeywordToken, "end"):
            statements.append(self.parse_statement())
        
        self.expect(KeywordToken, "end")

        return BlockNode(statements=statements)

    def parse_object_literal(self) -> ObjectLiteralNode:
        """
            object_literal = 
                | ("frozen" | "sealed")? "{" (object_literal_entry)* "}"
            ;
        """
        modifier = None

        if self.peek_is(KeywordToken, "sealed") or self.peek_is(KeywordToken, "frozen"):
            peeked = cast(KeywordToken, self.peek())
            match peeked.value:
                case "frozen":
                    modifier = "frozen"
                case "sealed":
                    modifier = "sealed"
                case _:
                    raise self.error(f"Unexpected modifier {peeked.value}, expected 'frozen' or 'sealed'")
            self.expect(KeywordToken)
        
        self.expect(ParenthesisToken, "{")

        entries = []

        while not self.peek_is(ParenthesisToken, "}"):
            entries.append(self.parse_object_literal_entry())

        self.expect(ParenthesisToken, "}")

        return ObjectLiteralNode(modifier=modifier, entries=entries)
    
    def parse_object_literal_entry(self) -> ObjectLiteralEntryNode:
        """
            object_literal_entry = 
                | "var"? (identifier | '[' expression ']') "=" expression comma?
                ;
        """
        is_var = False

        if self.peek_is(KeywordToken, "var"):
            self.expect(KeywordToken, "var")
            is_var = True
        
        # syntax sugar: { a: b } becomes { ["a"]: b }
        if self.peek_is(IdentifierToken):
            name_token = self.expect(IdentifierToken)
            name = StringLiteralNode(name_token.value)
        else:
            self.expect(ParenthesisToken, '[')
            name = self.parse_expression()
            self.expect(ParenthesisToken, ']')

        self.expect(OperatorToken, "=")
        value = self.parse_expression()

        if self.peek_is(PunctuationToken, ","):
            self.expect(PunctuationToken, ",")

        return ObjectLiteralEntryNode(name=name, value=value, is_var=is_var)

    def peek(self, offset=0) -> BaseToken:
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return self.tokens[-1]
    
    def peek_is(self, typ: type[Token], value=None) -> bool:
        token = self.peek()
        if type(token) is not typ:
            return False
        elif value is not None and hasattr(token, "value") and token.value != value: # type: ignore
            return False
        return True
    
    def consume(self):
        token = self.peek()

        if token is None:
            raise self.error(f"Unexpected end of input")
        token = self.tokens[self.pos]
        self.pos += 1
        return token
    
    T = TypeVar('T', bound=Token)

    def expect(self, typ: type[T], value=None) -> T:
        token = self.peek()

        if token is None:
            raise self.error(f"Unexpected end of input, expected {typ}")
        if type(token) is not typ:
            if value == None:
                raise self.error(f"Unexpected token {token}, expected {typ}")
            else:
                raise self.error(f"Unexpected token {token}, expected {typ} with value {value}")
        else:
            if value is not None and not hasattr(token, 'value'):
                raise self.error(f"Fatal: token {token} has no value attribute, cannot compare to expected value {value}")
            if value is not None and token.value != value: # type: ignore
                raise self.error(f"Unexpected token {token}, expected {typ} with value {value}")
        
            self.pos += 1
            return token # type: ignore
    
    def error(self, message: str):
        return Exception(f"Error at index {self.peek().position}: {message}")