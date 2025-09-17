from typing import Any, Dict, List
from parse import Node
from treewalk.spyobject import SpyObject
from treewalk.builtins import SpyObjectPrototype, make_spy_int, make_spy_string, SpyPrintFunction

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
        match node["type"]:
            case "program":
                for statement in node["body"]:
                    self.__eval(statement, scopes)
            case "let_statement":
                scopes[-1][node["name"]] = self.__eval(node["value"], scopes)
            case "unary_expression":
                match node["operator"]:
                    case "-":
                        return -self.__eval(node["right"], scopes)
                    case "+":
                        return -self.__eval(node["right"], scopes)
                    case "!":
                        return not self.__eval(node["right"], scopes)
                    case _:
                        raise Exception(f"Not implemented for unary operator {node['operator']}")
            case "binary_expression":
                if node["operator"] == ".":
                    left = self.__eval(node["left"], scopes)
                    if not isinstance(left, SpyObject):
                        raise Exception("Left side of dot operator must be an object")    
                    if node["right"]["type"] != "identifier":
                        raise Exception("Right side of dot operator must be an identifier")
                    return left.get(node["right"]["value"])
                
                left = self.__eval(node["left"], scopes)
                right = self.__eval(node["right"], scopes)
                print(left.props, "\n", right.props)
                match node["operator"]:
                    case "+":
                        return left.get("op_add").get("op_call")(left, right)
                    case "-":
                        return left.get("op_sub").get("op_call")(left, right)
                    case "*":
                        return left.get("op_mul").get("op_call")(left, right)
                    case "/":
                        return left.get("op_div").get("op_call")(left, right)
                    case "%":
                        return left.get("op_mod").get("op_call")(left, right)
                    case "==":
                        return left.get("op_eq").get("op_call")(left, right)
                    case "!=":
                        return left.get("op_ne").get("op_call")(left, right)
                    case "<":
                        return left.get("op_lt").get("op_call")(left, right)
                    case "<=":
                        return left.get("op_le").get("op_call")(left, right)
                    case ">":
                        return left.get("op_gt").get("op_call")(left, right)
                    case ">=":
                        return left.get("op_ge").get("op_call")(left, right)
            case "object_literal":
                obj = SpyObject()
                for prop in node["entries"]:
                    obj.set(prop["name"], self.__eval(prop["value"], scopes), prop["is_var"])
                obj.set("prototype", SpyObjectPrototype, is_var=False)
                return obj
            case "identifier":
                for scope in reversed(scopes):
                    if node["value"] in scope:
                        return scope[node["value"]]
                raise Exception(f"'{node['value']}' is not defined in any enclosing scopes")
            case "number_literal":
                return make_spy_int(node["value"])
            case "string_literal":
                return make_spy_string(node["value"])
            case "call_expression":
                callee = self.__eval(node["callee"], scopes)
                if not isinstance(callee, SpyObject) or not callee.has_key("op_call"):
                    raise Exception(f"'{node['name']}' is not callable")
                args = [self.__eval(arg, scopes) for arg in node["arguments"]]
                return callee.get("op_call")(callee, *args)