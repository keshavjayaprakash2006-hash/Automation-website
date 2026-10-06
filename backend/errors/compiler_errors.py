"""
AutoScript Compiler - Error Management Module
Defines structured error types, locations, and source snippet formatting for compiler diagnostics.
"""

from typing import Optional, Dict, Any

class CompilerError(Exception):
    def __init__(
        self,
        phase: str,  # 'LEXICAL', 'SYNTAX', 'SEMANTIC', 'RUNTIME'
        message: str,
        line: int,
        column: int,
        source_code: Optional[str] = None
    ):
        self.phase = phase
        self.message = message
        self.line = line
        self.column = column
        self.source_code = source_code
        super().__init__(self.format_message())

    def get_source_line(self) -> Optional[str]:
        if not self.source_code:
            return None
        lines = self.source_code.splitlines()
        if 1 <= self.line <= len(lines):
            return lines[self.line - 1]
        return None

    def format_snippet(self) -> str:
        line_str = self.get_source_line()
        if line_str is None:
            return ""
        prefix = f"{self.line} | "
        caret_indent = len(prefix) + max(0, self.column - 1)
        caret_line = " " * caret_indent + "^^^"
        return f"\n{prefix}{line_str}\n{caret_line}"

    def format_message(self) -> str:
        header = f"[{self.phase} ERROR] Line {self.line}, Column {self.column}: {self.message}"
        snippet = self.format_snippet()
        return header + snippet if snippet else header

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase": self.phase,
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "snippet": self.format_snippet(),
            "formatted": self.format_message()
        }
