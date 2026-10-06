"""
AutoScript Compiler - Token Definition
Defines Token classes and TokenType enumeration.
"""

from enum import Enum, auto
from typing import Any, Dict

class TokenType(Enum):
    COMMAND = "COMMAND"      # OPEN, GAP, PRESS, TYPE, LOOP, SET
    KEY = "KEY"              # TAB, ENTER, ESC, SPACE, BACKSPACE, UP, DOWN, LEFT, RIGHT, SHIFT, CTRL, ALT
    IDENTIFIER = "IDENTIFIER"# Variable identifiers
    STRING = "STRING"        # "text"
    NUMBER = "NUMBER"        # 5, 9
    EQUALS = "EQUALS"        # =
    LBRACE = "LBRACE"        # {
    RBRACE = "RBRACE"        # }
    NEWLINE = "NEWLINE"      # \n
    EOF = "EOF"              # End of file

class Token:
    def __init__(self, type_: TokenType, value: Any, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "value": str(self.value),
            "line": self.line,
            "column": self.column
        }

    def __repr__(self) -> str:
        return f"Token({self.type.value}, {repr(self.value)}, L{self.line}:C{self.column})"
