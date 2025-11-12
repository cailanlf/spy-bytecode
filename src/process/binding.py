from typing import Literal

from parse.parsenode import *

type DeclarationSite = LetStatementNode | ParameterNode

@dataclass
class Scope:
    type: Literal['global', 'block']
    names: dict[str, DeclarationSite]

class Resolver():
    scopes: list[Scope]

    def __init__(self):
        self.scopes = []

    def resolve(self, root: ProgramNode):
        self._resolve(root)

    def _resolve(self, node: Node):
        match node:
            case ProgramNode():
                global_scope = Scope('global', {})
                self.scopes.append(global_scope)

                for statement in node.statements:
                    self._resolve(statement)

            case LetStatementNode():
                self._resolve(node.value)
                name = node.name.token.content
                self.scopes[-1].names[name] = node

            case ExpressionStatementNode():
                self._resolve(node.expr)

            case IdentifierExpressionNode():
                raise NotImplementedError()

            case ObjectLiteralExpressionNode():
                for entry in node.contents:
                    self._resolve(entry)

            case ObjectLiteralEntryNode():
                self._resolve(node.value)

            case BinaryExpressionNode():
                self._resolve(node.left)
                self._resolve(node.right)

            case PrefixExpressionNode() | PostfixExpressionNode():
                self._resolve(node.operand)

            case AssignmentExpressionNode():
                raise NotImplementedError()
                self._resolve(node.value)

            case (NumberLiteralExpressionNode() 
                | NumberLiteralNode() 
                | IdentifierNode()
                | StringLiteralExpressionNode()
                | StringLiteralNode()
                | BoolLiteralExpressionNode()
                | BoolLiteralNode()):
                pass

            case BlockNode():
                for statement in node.statements:
                    self._resolve(statement)

            case IfElseExpressionNode():
                # introduce scope
                raise NotImplementedError()
            
            case LoopExpressionNode():
                # introduce scope
                raise NotImplementedError()
            
            case BreakExpressionNode():
                if node.expr is not None:
                    self._resolve(node.expr)

            case ContinueExpressionNode():
                pass

            case IndexExpressionNode():
                self._resolve(node.left)
                self._resolve(node.index)

            case ArgumentListNode():
                for arg in node.arguments:
                    self._resolve(arg)

            case ArgumentNode():
                self._resolve(node.expr)

            case FunctionLiteralExpressionNode():
                raise NotImplementedError()
            
            case ParameterListNode():
                raise NotImplementedError()
            
            case ParameterNode():
                raise NotImplementedError()