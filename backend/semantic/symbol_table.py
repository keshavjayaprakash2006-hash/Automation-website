"""
AutoScript Compiler - Symbol Table
Manages variable declarations, scopes, types, values, and symbol lookup for semantic analysis.
"""

from typing import Dict, Any, List, Optional

class Symbol:
    def __init__(self, name: str, symbol_type: str, value: Any, scope: str = "global", line: int = 1, column: int = 1):
        self.name = name
        self.type = symbol_type  # 'NUMBER' or 'STRING'
        self.value = value
        self.scope = scope
        self.line = line
        self.column = column

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "value": str(self.value),
            "scope": self.scope,
            "line": self.line,
            "column": self.column
        }


class SymbolTable:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}

    def define(self, name: str, symbol_type: str, value: Any, scope: str = "global", line: int = 1, column: int = 1) -> Symbol:
        sym = Symbol(name, symbol_type, value, scope, line, column)
        self.symbols[name] = sym
        return sym

    def lookup(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

    def is_defined(self, name: str) -> bool:
        return name in self.symbols

    def to_list(self) -> List[Dict[str, Any]]:
        return [sym.to_dict() for sym in self.symbols.values()]
