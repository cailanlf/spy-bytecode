from typing import get_args, cast

from lex.token import *
from parse.parsenode import *

class Parser:
    tokens: list[Token]
    pos: int

    def __init__(self, tokens: list[Token]):
        self.pos = 0
        self.tokens = tokens

    precedence_assignment = 0
    precedence_or = 1
    precedence_and = 2
    precedence_not = 3
    precedence_comparison = 4
    precedence_additive = 5
    precedence_multiplicative = 6
    precedence_unary_minus = 7
    precedence_index_call = 8

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
    def get_prefix_precedence(token: Token):        
        if token.type == 'minus' or token.type == 'plus':
            return Parser.unary_power(Parser.precedence_unary_minus)
        if token.type == 'bang':
            return Parser.unary_power(Parser.precedence_not)
        else: return 0

    @staticmethod
    def get_postfix_precedence(token: Token):
        if token.type == 'lbracket' or token.type == 'lparen':
            return Parser.unary_power(Parser.precedence_index_call)
        return 0
    
    @staticmethod
    def get_binary_precedence(token: Token): 
        if token.type == "asterisk" or token.type == "slash":
            return Parser.binary_left_associative_powers(Parser.precedence_multiplicative)
        elif token.type == "plus" or token.type == "minus":
            return Parser.binary_left_associative_powers(Parser.precedence_additive)
        elif token.type == "period":
            return Parser.binary_left_associative_powers(Parser.precedence_index_call)
        elif token.type in {'less', 'greater', 'lessequals', 'greaterequals', 'equalsequals', 'bangequals'}:
            return Parser.binary_left_associative_powers(Parser.precedence_comparison)
        elif token.type == "equals":
            return Parser.binary_left_associative_powers(Parser.precedence_assignment)
        else:
            return (0, 0)

    def parse_program(self) -> ProgramNode:
        # program = top-level-statement+;
        statements = []
        while not self.peek_is('eof'):
            statements.append(self.parse_top_level_statement())
        return ProgramNode(statements)

    def parse_top_level_statement(self) -> TopLevelStatement:
        if self.peek_is('keyword', Keyword_let):
            return self.parse_let_statement()
        else:
            return self.parse_expression_statement()
        
    def parse_statement(self) -> Statement:
        if self.peek_is('keyword', Keyword_let):
            return self.parse_let_statement()
        else:
            return self.parse_expression_statement()
        
    def parse_let_statement(self) -> LetStatementNode:
        self.expect('keyword', Keyword_let)
        if self.peek_is('keyword', Keyword_var):
            self.consume()
            mutable = True
        else:
            mutable = False
        name = self.parse_identifier()
        self.expect('equals')
        expr = self.parse_expression()
        return LetStatementNode(name, expr, mutable)
    
    def parse_expression_statement(self) -> ExpressionStatementNode:
        expr = self.parse_expression()
        return ExpressionStatementNode(expr)
    
    def parse_expression(self, min_bp: int = 0) -> Expression:
        if self.peek_is('keyword', Keyword_if):
            return self.parse_if_else_expression()
        elif self.peek_is('keyword', Keyword_loop):
            return self.parse_loop_expression()
        elif self.peek_is('keyword', Keyword_break):
            return self.parse_break_expression()
        elif self.peek_is('keyword', Keyword_continue):
            return self.parse_continue_expression()
        
        pre_bp = Parser.get_prefix_precedence(self.peek())

        if pre_bp != 0 and pre_bp > min_bp:
            op = self.consume()
            if self.peek().whitespace_before:
                raise Exception("while parsing prefix operator: unexpected whitespace")
            if op.type not in get_args(PrefixOperator):
                raise Exception(f"while parsing prefix operator: invalid operator {op}")
            
            op = cast(PrefixOperator, op.type)
            expr = self.parse_expression(pre_bp)
            
            left = PrefixExpressionNode(expr, op)
        else:
            left = self.parse_atomic_expression()
        
        while True:
            post_bp = Parser.get_postfix_precedence(self.peek())

            if post_bp == 0 or post_bp < min_bp:
                break

            op = self.consume()
            expr = left

            if op.type == 'lparen':
                # Call operator
                args = self.parse_argument_list()
                self.expect('rparen')
                
                left = CallExpressionNode(expr, args)
            elif op.type == "lbracket":
                # Index operator
                expr = self.parse_expression()
                self.expect('rbracket')

                left = IndexExpressionNode(left, expr)
            else:
                if op.whitespace_before:
                    raise Exception("while parsing postfix operator: unexpected whitespace")
                if op.type not in get_args(PostfixOperator):
                    raise Exception(f"while parsing postfix operator: invalid operator {op}")
                
                op = cast(PostfixOperator, op.type)
                left = PostfixExpressionNode(expr, op)

        while True:
            (left_bp, right_bp) = Parser.get_binary_precedence(self.peek())

            if self.peek().whitespace_before != self.peek().whitespace_after:
                left_bp, right_bp = 0, 0
            if left_bp == 0 or left_bp < min_bp:
                break

            op = self.consume()
            right = self.parse_expression(right_bp)

            if op.type == 'equals':
                if not isinstance(left, IdentifierExpressionNode):
                    raise Exception("left side of assignment must be identifier")
                left = AssignmentExpressionNode(left, right)
            elif op.type not in get_args(BinaryOperator):
                raise Exception(f"while parsing binary operator: invalid operator {op}")
            else:
                op = cast(BinaryOperator, op.type)
                left = BinaryExpressionNode(left, right, op)
        
        return left

    def parse_argument_list(self) -> ArgumentListNode:
        arguments = []
        if not self.peek_is('rparen'):    
            arguments.append(self.parse_argument())
            
            while self.peek_is('comma'):
                self.expect('comma')

                if self.peek_is('rparen'):
                    break

                arguments.append(self.parse_argument())
        return ArgumentListNode(tuple(arguments))
    
    def parse_argument(self) -> ArgumentNode:
        return ArgumentNode(self.parse_expression()) 
    
    def parse_parameter_list(self) -> ParameterListNode:
        params = []
        if not self.peek_is('pipe'):    
            params.append(self.parse_parameter())
            
            while self.peek_is('comma'):
                self.expect('comma')

                if self.peek_is('pipe'):
                    break

                params.append(self.parse_parameter())
        return ParameterListNode(tuple(params))

    def parse_parameter(self) -> ParameterNode:
        return ParameterNode(self.parse_identifier())

    def parse_atomic_expression(self) -> AtomicExpression:
        if self.peek_is('number'):
            return self.parse_number_literal_expression()
        elif self.peek_is('identifier'):
            return self.parse_identifier_expression()
        elif self.peek_is('lcurly'):
            return self.parse_object_literal_expression()
        elif self.peek_is('string'):
            return self.parse_string_literal_expression()
        elif self.peek_is('pipe'):
            return self.parse_function_literal_expression()
        elif self.peek_is('keyword', Keyword_true) or \
                self.peek_is('keyword', Keyword_false):
            return self.parse_bool_literal_expression()
        else:
            raise Exception(f"while parsing atomic: encountered unexpected token {self.peek()}")

    def parse_number_literal_expression(self) -> NumberLiteralExpressionNode:
        number = self.parse_number_literal()
        return NumberLiteralExpressionNode(number)
    
    def parse_identifier_expression(self) -> IdentifierExpressionNode:
        ident = self.parse_identifier()
        return IdentifierExpressionNode(ident)
    
    def parse_string_literal_expression(self) -> StringLiteralExpressionNode:
        string = self.parse_string_literal()
        return StringLiteralExpressionNode(string)
    
    def parse_bool_literal_expression(self) -> BoolLiteralExpressionNode:
        bool = self.parse_bool_literal()
        return BoolLiteralExpressionNode(bool)
    
    def parse_string_literal(self) -> StringLiteralNode:
        string = self.expect('string')
        return StringLiteralNode(string)
    
    def parse_bool_literal(self) -> BoolLiteralNode:
        bool = self.expect('keyword')

        if bool.content != Keyword_true and bool.content != Keyword_false:
            raise Exception(f"parse error: got wrong keyword for boolean. expected {Keyword_true} or {Keyword_false} but got {bool.content}")
        return BoolLiteralNode(bool)
    
    def parse_object_literal_expression(self) -> ObjectLiteralExpressionNode:
        self.expect('lcurly')
        entries = []
        while not self.peek_is('rcurly'):
            entry = self.parse_object_literal_entry()
            entries.append(entry)
        self.expect('rcurly')
        return ObjectLiteralExpressionNode(entries)
    
    def parse_object_literal_entry(self) -> ObjectLiteralEntryNode:
        mutable = True
        if self.peek_is('keyword', Keyword_var):
            self.consume()
            mutable = True
        elif self.peek_is('keyword', Keyword_const):
            self.consume()
            mutable = False
            print("parse: warn: immutable object keys not yet implemented")

        left = self.parse_expression()        
        self.expect('colon')
        right = self.parse_expression()
        return ObjectLiteralEntryNode(left, right, mutable)
        
    def parse_number_literal(self) -> NumberLiteralNode:
        number = self.expect('number')
        return NumberLiteralNode(number)
    
    def parse_identifier(self) -> IdentifierNode:
        ident = self.expect('identifier')
        return IdentifierNode(ident)
    
    def parse_function_literal_expression(self) -> FunctionLiteralExpressionNode:
        self.expect('pipe')
        params = self.parse_parameter_list()
        self.expect('pipe')
        self.expect('colon')
        statements = []
        while not self.peek_is('keyword', Keyword_end):
            statements.append(self.parse_statement())
        self.expect('keyword', Keyword_end)
        return FunctionLiteralExpressionNode(params, BlockNode(tuple(statements)))
    
    def parse_if_else_expression(self) -> IfElseExpressionNode:
        cases = []
        
        self.expect('keyword', Keyword_if)
        cond = self.parse_expression()
        self.expect('colon')
        statements = []
        while not (self.peek_is("keyword", Keyword_elif) 
                or self.peek_is("keyword", Keyword_else)
                or self.peek_is("keyword", Keyword_end)):
            statements.append(self.parse_statement())
        
        cases.append((cond, BlockNode(tuple(statements))))

        while self.peek_is('keyword', Keyword_elif):
            self.expect('keyword', Keyword_elif)
            cond = self.parse_expression()
            self.expect('colon')
            statements = []
            while not (self.peek_is("keyword", Keyword_elif) 
                    or self.peek_is("keyword", Keyword_else)
                    or self.peek_is("keyword", Keyword_end)):
                statements.append(self.parse_statement())
            cases.append((cond, BlockNode(tuple(statements))))

        if self.peek_is('keyword', Keyword_else):
            self.expect('keyword', Keyword_else)
            self.expect('colon')
            statements = []
            while not self.peek_is("keyword", "end"):
                statements.append(self.parse_statement())
            cases.append((None, BlockNode(tuple(statements))))
        self.expect('keyword', Keyword_end)

        return IfElseExpressionNode(tuple(cases))
    
    def parse_loop_expression(self) -> LoopExpressionNode:
        self.expect('keyword', Keyword_loop)
        self.expect('colon')

        statements: list[Statement] = []

        while not self.peek_is('keyword', Keyword_end):
            statements.append(self.parse_statement())
        self.expect('keyword', Keyword_end)
        return LoopExpressionNode(BlockNode(tuple(statements)))
    
    def parse_break_expression(self) -> BreakExpressionNode:
        self.expect('keyword', Keyword_break)
        expr = None
        if self.peek_is('keyword', Keyword_with):
            self.expect('keyword', Keyword_with)
            expr = self.parse_expression()

        return BreakExpressionNode(expr)
    
    def parse_continue_expression(self) -> ContinueExpressionNode:
        self.expect('keyword', Keyword_continue)
        
        return ContinueExpressionNode()
    
    def peek(self):
        if self.pos < len(self.tokens) - 1:
            return self.tokens[self.pos]
        else:
            return self.tokens[-1]
        
    def peek_is(self, type: TokenType, value: str|None = None):
        peeked = self.peek()
        if peeked.type != type:
            return False
        elif value is not None and peeked.content != value:
            return False
        else:
            return True
        
    def consume(self):
        if self.pos < len(self.tokens) - 1:
            current = self.tokens[self.pos]
            self.pos += 1
            return current
        else:
            raise Exception("consumed beyond end of token stream")
    
    def expect(self, type: TokenType, value: str|None = None):
        peeked = self.peek()
        if peeked.type != type:
            raise Exception(f"Expected token of type {type}, but got token of type {peeked.type}")
        elif value is not None and peeked.content != value:
            raise Exception(f"Expected token of type {peeked} to have value '{value}', but got value '{peeked.content}'")
        else:
            return self.consume()