from typing import Callable

from treewalk.spyobject import SpyObject

def make_spy_int(value: int) -> SpyObject:
    obj = SpyObject()
    obj.set("value", value, is_var=False)
    obj.set("prototype", SpyNumberPrototype, is_var=False)
    obj.freeze()
    return obj

def make_spy_string(value: str) -> SpyObject:
    obj = SpyObject()
    obj.set("value", value, is_var=False)
    obj.set("prototype", SpyStringPrototype, is_var=False)
    obj.freeze()
    return obj

def make_spy_builtin(func: Callable[[SpyObject], SpyObject]) -> SpyObject:
    obj = SpyObject()
    obj.set("op_call", func, is_var=False)
    obj.set("prototype", SpyObjectPrototype, is_var=False)
    obj.freeze()
    return obj

SpyObjectPrototype = SpyObject()
SpyObjectPrototype.set("hash", make_spy_builtin(lambda self: make_spy_int(id(self))), is_var=False)
SpyObjectPrototype.set("op_eq", make_spy_builtin(lambda self,other: SpyTrue if self is other else SpyFalse), is_var=False)
SpyObjectPrototype.freeze()

SpyNone = SpyObject()
SpyNone.set("value", None, is_var=False)
SpyNone.set("prototype", SpyObjectPrototype, is_var=False)
SpyNone.freeze()

SpyTrue = SpyObject()
SpyTrue.set("value", True, is_var=False)
SpyTrue.set("prototype", SpyObjectPrototype, is_var=False)
SpyTrue.freeze()

SpyFalse = SpyObject()
SpyFalse.set("value", False, is_var=False)
SpyFalse.set("prototype", SpyObjectPrototype, is_var=False)
SpyFalse.freeze()

SpyNumberPrototype = SpyObject()
SpyNumberPrototype.set("op_add", make_spy_builtin(lambda self,other: make_spy_int(self.get("value") + other.get("value"))), is_var=False)
SpyNumberPrototype.set("op_sub", make_spy_builtin(lambda self,other: make_spy_int(self.get("value") - other.get("value"))), is_var=False)
SpyNumberPrototype.set("op_mul", make_spy_builtin(lambda self,other: make_spy_int(self.get("value") * other.get("value"))), is_var=False)
SpyNumberPrototype.set("op_div", make_spy_builtin(lambda self,other: make_spy_int(self.get("value") // other.get("value"))), is_var=False)
SpyNumberPrototype.set("op_mod", make_spy_builtin(lambda self,other: make_spy_int(self.get("value") % other.get("value"))), is_var=False)
SpyNumberPrototype.set("op_eq", make_spy_builtin(lambda self,other: SpyTrue if self.get("value") == other.get("value") else SpyFalse), is_var=False)
SpyNumberPrototype.set("protoype", SpyObjectPrototype, is_var=False)
SpyNumberPrototype.freeze()

SpyStringPrototype = SpyObject()
SpyStringPrototype.set("op_add", make_spy_builtin(lambda self,other: make_spy_string(self.get("value") + other.get("value"))), is_var=False)
SpyStringPrototype.set("op_eq", make_spy_builtin(lambda self,other: SpyTrue if self.get("value") == other.get("value") else SpyFalse), is_var=False)
SpyStringPrototype.set("length", make_spy_builtin(lambda self: make_spy_int(len(self.get("value")))), is_var=False)
SpyStringPrototype.set("prototype", SpyObjectPrototype, is_var=False)
SpyStringPrototype.freeze()

SpyPrintFunction = make_spy_builtin(lambda self,arg: print(arg.get("value")) or SpyNone)