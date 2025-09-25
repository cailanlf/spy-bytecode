from typing import Dict, TypedDict

class SpyBytes:
    value: bytearray

class SpyObjectEntry(TypedDict):
    value: 'SpyObject'
    is_var: bool

class SpyObject:
    is_frozen: bool = False
    is_sealed: bool = False

    def __init__(self):
        self.props: Dict[SpyObject, SpyObjectEntry] = {}

    def freeze(self):
        self.is_frozen = True

    def seal(self):
        self.is_sealed = True

    def set(self, key: 'SpyObject', value: 'SpyObject', is_var: bool):
        if self.is_frozen:
            raise Exception("Cannot modify frozen object")
        if self.is_sealed and key not in self.props:
            raise Exception("Cannot add new properties to sealed object")
        if key in self.props and not self.props[key]["is_var"]:
            raise Exception(f"Cannot reassign constant property '{key}'")
        self.props[key] = {
            "value": value,
            "is_var": is_var
        }

    def get(self, key: 'SpyObject') -> 'SpyObject':
        from treewalk.builtins import make_spy_string

        if key not in self.props:
            if make_spy_string("prototype") in self.props:
                return self.props[make_spy_string("prototype")]["value"].get(key)
            raise Exception(f"Property '{key}' not found")
        return self.props[key]["value"]
    
    def has_key(self, key: str) -> bool:
        from treewalk.builtins import make_spy_string
        
        if key in self.props:
            return True
        if make_spy_string("prototype") in self.props:
            return self.props[make_spy_string("prototype")]["value"].has_key(key)
        return False
    
    def delete(self, key: 'SpyObject'):
        if self.is_frozen:
            raise Exception("Cannot modify frozen object")
        if self.is_sealed:
            raise Exception("Cannot delete properties from sealed object")
        if key not in self.props:
            raise Exception(f"Property '{key}' not found")
        del self.props[key]

    def __hash__(self):
        return self.get(make_spy_string("hash")).get("op_call")(self) # type: ignore

    def __eq__(self, other):
        from treewalk.builtins import SpyTrue
        return self.get(make_spy_string("op_eq")).get("op_call")(self, other) == SpyTrue # type: ignore