"""
AutoScript Compiler - Intermediate Representation (IR) Generator
Translates validated AST nodes into a flat linear Quadruple/Instruction-based IR format.
"""

from typing import List, Dict, Any, Union
from backend.ast.nodes import (
    ProgramNode, OpenNode, GapNode, TypeNode, PressNode,
    LoopNode, SetNode, LiteralNode, VariableNode, ASTNode
)
from backend.semantic.symbol_table import SymbolTable

class IRInstruction:
    def __init__(self, index: int, op: str, args: List[Any], line: int = 1):
        self.index = index
        self.op = op
        self.args = args
        self.line = line

    def format_args(self) -> str:
        formatted_args = []
        for arg in self.args:
            if isinstance(arg, str) and not arg.isdigit() and not arg.isupper():
                formatted_args.append(f'"{arg}"')
            else:
                formatted_args.append(str(arg))
        return " ".join(formatted_args)

    def to_string(self) -> str:
        args_str = self.format_args()
        return f"{self.index}. {self.op} {args_str}".strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "op": self.op,
            "args": self.args,
            "line": self.line,
            "instruction": self.to_string()
        }


class IRGenerator:
    def __init__(self, ast: ProgramNode, symbol_table: SymbolTable = None):
        self.ast = ast
        self.symbol_table = symbol_table
        self.instructions: List[IRInstruction] = []
        self.instr_counter = 1

    def resolve_expr(self, expr_node: ASTNode) -> Any:
        if isinstance(expr_node, LiteralNode):
            return expr_node.value
        elif isinstance(expr_node, VariableNode):
            if self.symbol_table and self.symbol_table.is_defined(expr_node.name):
                sym = self.symbol_table.lookup(expr_node.name)
                return sym.value if sym.value is not None else f"${expr_node.name}"
            return f"${expr_node.name}"
        return str(expr_node)

    def emit(self, op: str, args: List[Any], line: int = 1) -> IRInstruction:
        instr = IRInstruction(self.instr_counter, op, args, line)
        self.instructions.append(instr)
        self.instr_counter += 1
        return instr

    def generate(self) -> List[IRInstruction]:
        self.instructions = []
        self.instr_counter = 1
        for stmt in self.ast.statements:
            self.visit_statement(stmt)
        return self.instructions

    def visit_statement(self, node: ASTNode):
        if isinstance(node, SetNode):
            val = self.resolve_expr(node.value)
            self.emit("SET_VAR", [node.name, val], line=node.line)

        elif isinstance(node, OpenNode):
            url = self.resolve_expr(node.url)
            self.emit("OPEN_URL", [url], line=node.line)

        elif isinstance(node, GapNode):
            dur = self.resolve_expr(node.duration)
            self.emit("WAIT", [dur], line=node.line)

        elif isinstance(node, TypeNode):
            txt = self.resolve_expr(node.text)
            self.emit("TYPE_TEXT", [txt], line=node.line)

        elif isinstance(node, PressNode):
            key = node.key.upper()
            cnt = self.resolve_expr(node.count)
            self.emit("PRESS_KEY", [key, cnt], line=node.line)

        elif isinstance(node, LoopNode):
            cnt = self.resolve_expr(node.count)
            self.emit("LOOP_START", [cnt], line=node.line)
            for body_stmt in node.body:
                self.visit_statement(body_stmt)
            self.emit("LOOP_END", [], line=node.line)
