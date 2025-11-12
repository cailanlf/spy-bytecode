from typing import Literal

from parse.parsenode import *

type DeclarationSite = LetStatementNode | ParameterNode

@dataclass
class Scope:
    type: Literal['global', 'block']
    names: dict[str, DeclarationSite]
    parent: FunctionLiteralExpressionNode | None

@dataclass
class BindingInfo:
    decl: DeclarationSite
    type: Literal['global', 'block', 'parameter']

class Resolver():
    scopes: list[Scope]
    bindings: dict[IdentifierExpressionNode, BindingInfo]
    root: ProgramNode

    def __init__(self, root: ProgramNode):
        self.scopes = []
        self.bindings = {}
        self.root = root

    def resolve(self):
        self._resolve(self.root)

    def _resolve(self, node: Node):
        match node:
            case ProgramNode():
                global_scope = Scope('global', names = {}, parent = None)
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
                name = node.identifier.token.content

                for scope in reversed(self.scopes):
                    if name in scope.names:
                        self.bindings[node] = BindingInfo(
                            decl = scope.names[name],
                            type = scope.type,
                        )
                        break
                else:
                    raise NameError(f"Name {name} cannot be resolved.")

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
                for case in node.cases:
                    condition, block = case
                    
                    if condition is not None:
                        self._resolve(condition)
                    
                    self.scopes.append(
                        Scope(
                            type = 'block',
                            names = {},
                            parent = self.scopes[-1].parent
                        )
                    )

                    self._resolve(block)

                    self.scopes.pop()
            
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