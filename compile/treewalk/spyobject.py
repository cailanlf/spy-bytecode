from typing import Dict

class SpyObject:
    is_frozen: bool = False
    is_sealed: bool = False

    def __init__(self):
        self.props: Dict[str, Dict[str, SpyObject]] = {}

    def freeze(self):
        self.is_frozen = True

    def seal(self):
        self.is_sealed = True

    def set(self, key: str, value: 'SpyObject', is_var: bool):
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

    def get(self, key: str) -> 'SpyObject':
        if key not in self.props:
            if "prototype" in self.props:
                return self.props["prototype"]["value"].get(key)
            raise Exception(f"Property '{key}' not found")
        return self.props[key]["value"]
    
    def has_key(self, key: str) -> bool:
        if key in self.props:
            return True
        if "prototype" in self.props:
            return self.props["prototype"]["value"].has_key(key)
        return False
    
    def delete(self, key: str):
        if self.is_frozen:
            raise Exception("Cannot modify frozen object")
        if self.is_sealed:
            raise Exception("Cannot delete properties from sealed object")
        if key not in self.props:
            raise Exception(f"Property '{key}' not found")
        del self.props[key]