from typing import Any, Dict, List
from parse import Node

from treewalk.spyobject import SpyObject
from treewalk.builtins import SpyObjectPrototype, make_spy_int, make_spy_string, SpyPrintFunction

from parsenodes import *

class TreeWalker:
    """
    Implements a simple tree walking interpreter
    """

    def __init__(self, root: Node):
        self.root: Node = root

    def evaluate(self) -> Any:
        return self.__eval(self.root, [{
            "print": SpyPrintFunction
        }])

    def __eval(self, node: Node, scopes: List[Dict[str, Any]]) -> SpyObject:
        match node:
            case ProgramNode():
                return self.__eval(node.body, scopes)
            
            case LetStatementNode():
                if type(node.left) is not IdentifierNode:
                    raise Exception("Left hand of let statement must be an identifier")
                scopes[-1][node.left.value] = self.__eval(node.right, scopes)

            case UnaryExpressionNode():
                operand = self.__eval(node.operand, scopes)
                match node.operator:
                    case "-":
                        return operand.get("op_neg").get("op_call")(operand) # type: ignore
                    case "+":
                        return operand.get("op_pos").get("op_call")(operand) # type: ignore
                    case "!":
                        return operand.get("op_not").get("op_call")(operand) # type: ignore
                    case _:
                        raise Exception(f"Not implemented for unary operator {node.operator}")
                    
            case BinaryExpressionNode():
                if node.operator == ".":
                    left = self.__eval(node.left, scopes)
                    if not isinstance(left, SpyObject):
                        raise Exception("Left side of dot operator must be an object")    
                    if not isinstance(node.right, IdentifierNode):
                        raise Exception("Right side of dot operator must be an identifier")
                    return left.get(make_spy_string(node.right.value))
                
                left = self.__eval(node.left, scopes)
                right = self.__eval(node.right, scopes)
                
                match node.operator:
                    case "+":
                        return left.get("op_add").get("op_call")(left, right) # type: ignore
                    case "-":
                        return left.get("op_sub").get("op_call")(left, right) # type: ignore
                    case "*":
                        return left.get("op_mul").get("op_call")(left, right) # type: ignore
                    case "/":
                        return left.get("op_div").get("op_call")(left, right) # type: ignore
                    case "%":
                        return left.get("op_mod").get("op_call")(left, right) # type: ignore
                    case "==":
                        return left.get("op_eq").get("op_call")(left, right) # type: ignore
                    case "!=":
                        return left.get("op_ne").get("op_call")(left, right) # type: ignore
                    case "<":
                        return left.get("op_lt").get("op_call")(left, right) # type: ignore
                    case "<=":
                        return left.get("op_le").get("op_call")(left, right) # type: ignore
                    case ">":
                        return left.get("op_gt").get("op_call")(left, right) # type: ignore
                    case ">=":
                        return left.get("op_ge").get("op_call")(left, right) # type: ignore
                    case _:
                        raise Exception(f"Not implemented for binary operator {node.operator}")
                    
            case ObjectLiteralNode():
                obj = SpyObject()
                for prop in node.entries:
                    name = prop.name
                    if type(name) is str:
                        name = make_spy_string(name)
                    else:
                        name = self.__eval(name, scopes) # type: ignore
                    obj.set(name, self.__eval(prop.value, scopes), prop.is_var)
                obj.set(make_spy_string("prototype"), SpyObjectPrototype, is_var=False)
                return obj
            
            case IdentifierNode():
                for scope in reversed(scopes):
                    if node.value in scope:
                        return scope[node.value]
                raise Exception(f"'{node.value}' is not defined in any enclosing scopes")
            
            case NumberLiteralNode():
                return make_spy_int(int(node.value))
            
            case StringLiteralNode():
                return make_spy_string(node.value)
            
            case CallExpressionNode():
                callee = self.__eval(node.callee, scopes)
                if not isinstance(callee, SpyObject) or not callee.has_key("op_call"):
                    raise Exception(f"'{node.callee}' is not callable")
                args = [self.__eval(arg, scopes) for arg in node.arguments]
                return callee.get("op_call")(callee, *args) # type: ignore