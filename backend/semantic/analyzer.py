"""
AutoScript Compiler - Semantic Analyzer
Enforces semantic rules, type safety, range constraints, scope checks, and symbol table population.
"""

from typing import List, Optional
from backend.ast.nodes import (
    ProgramNode, OpenNode, GapNode, TypeNode, PressNode,
    LoopNode, SetNode, LiteralNode, VariableNode, ASTNode
)
from backend.semantic.symbol_table import SymbolTable, Symbol
from backend.errors.compiler_errors import CompilerError

SUPPORTED_KEYS = {
    "TAB", "ENTER", "ESC", "SPACE", "BACKSPACE",
    "UP", "DOWN", "LEFT", "RIGHT", "SHIFT", "CTRL", "ALT"
}

class SemanticAnalyzer:
    def __init__(self, ast: ProgramNode, source_code: str = ""):
        self.ast = ast
        self.source_code = source_code
        self.symbol_table = SymbolTable()
        self.errors: List[CompilerError] = []

    def error(self, message: str, node: ASTNode):
        err = CompilerError("SEMANTIC", message, node.line, node.column, self.source_code)
        self.errors.append(err)
        raise err

    def analyze(self) -> SymbolTable:
        """Analyzes the AST and populates the SymbolTable."""
        self.errors = []
        self.symbol_table = SymbolTable()
        self.visit_program(self.ast, scope="global")
        return self.symbol_table

    def visit_program(self, node: ProgramNode, scope: str = "global"):
        for stmt in node.statements:
            self.visit_statement(stmt, scope=scope)

    def visit_statement(self, node: ASTNode, scope: str = "global"):
        if isinstance(node, SetNode):
            self.visit_set(node, scope=scope)
        elif isinstance(node, OpenNode):
            self.visit_open(node, scope=scope)
        elif isinstance(node, GapNode):
            self.visit_gap(node, scope=scope)
        elif isinstance(node, TypeNode):
            self.visit_type(node, scope=scope)
        elif isinstance(node, PressNode):
            self.visit_press(node, scope=scope)
        elif isinstance(node, LoopNode):
            self.visit_loop(node, scope=scope)
        else:
            self.error(f"Unknown AST node type '{node.node_type}'", node)

    def evaluate_expression_type_and_val(self, expr_node: ASTNode, scope: str = "global") -> tuple[str, Optional[object]]:
        if isinstance(expr_node, LiteralNode):
            return expr_node.literal_type, expr_node.value
        elif isinstance(expr_node, VariableNode):
            sym = self.symbol_table.lookup(expr_node.name)
            if not sym:
                self.error(f"Undeclared variable identifier '{expr_node.name}'", expr_node)
            return sym.type, sym.value
        else:
            self.error(f"Invalid expression node '{expr_node.node_type}'", expr_node)

    def visit_set(self, node: SetNode, scope: str = "global"):
        val_type, val_value = self.evaluate_expression_type_and_val(node.value, scope=scope)
        self.symbol_table.define(
            name=node.name,
            symbol_type=val_type,
            value=val_value,
            scope=scope,
            line=node.line,
            column=node.column
        )

    def visit_open(self, node: OpenNode, scope: str = "global"):
        url_type, url_val = self.evaluate_expression_type_and_val(node.url, scope=scope)
        if url_type != "STRING":
            self.error(f"OPEN command requires a STRING argument, found '{url_type}'", node)
        if url_val is not None and isinstance(url_val, str) and not url_val.strip():
            self.error("OPEN URL cannot be empty", node)

    def visit_gap(self, node: GapNode, scope: str = "global"):
        dur_type, dur_val = self.evaluate_expression_type_and_val(node.duration, scope=scope)
        if dur_type != "NUMBER":
            self.error(f"GAP duration requires a NUMBER argument, found '{dur_type}'", node)
        if dur_val is not None and isinstance(dur_val, (int, float)):
            if dur_val <= 0:
                self.error(f"GAP duration must be a positive number (> 0), found {dur_val}", node)

    def visit_type(self, node: TypeNode, scope: str = "global"):
        txt_type, txt_val = self.evaluate_expression_type_and_val(node.text, scope=scope)
        if txt_type != "STRING":
            self.error(f"TYPE command requires a STRING argument, found '{txt_type}'", node)

    def visit_press(self, node: PressNode, scope: str = "global"):
        key_upper = node.key.upper()
        if key_upper not in SUPPORTED_KEYS:
            self.error(f"Unsupported key '{node.key}'. Supported keys: {', '.join(sorted(SUPPORTED_KEYS))}", node)

        count_type, count_val = self.evaluate_expression_type_and_val(node.count, scope=scope)
        if count_type != "NUMBER":
            self.error(f"PRESS repeat count requires a NUMBER argument, found '{count_type}'", node)
        if count_val is not None and isinstance(count_val, (int, float)):
            if count_val <= 0:
                self.error(f"PRESS repeat count must be a positive integer (>= 1), found {count_val}", node)

    def visit_loop(self, node: LoopNode, scope: str = "global"):
        count_type, count_val = self.evaluate_expression_type_and_val(node.count, scope=scope)
        if count_type != "NUMBER":
            self.error(f"LOOP count requires a NUMBER argument, found '{count_type}'", node)
        if count_val is not None and isinstance(count_val, (int, float)):
            if count_val <= 0:
                self.error(f"LOOP count must be a positive integer (> 0), found {count_val}", node)

        loop_scope = f"loop_L{node.line}"
        for stmt in node.body:
            self.visit_statement(stmt, scope=loop_scope)
