"""
AutoScript Compiler - Abstract Syntax Tree (AST) Nodes
Defines node classes for the compiler AST hierarchy with serialization and tree visualization methods.
"""

from typing import List, Dict, Any, Union

class ASTNode:
    def __init__(self, node_type: str, line: int = 1, column: int = 1):
        self.node_type = node_type
        self.line = line
        self.column = column

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError

    def to_tree_dict(self) -> Dict[str, Any]:
        """Returns a hierarchical dictionary structure for UI parse/AST tree rendering."""
        return self.to_dict()


class ProgramNode(ASTNode):
    def __init__(self, statements: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__("Program", line, column)
        self.statements = statements

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Program",
            "line": self.line,
            "column": self.column,
            "statements": [stmt.to_dict() for stmt in self.statements]
        }

    def to_tree_dict(self) -> Dict[str, Any]:
        return {
            "name": "Program",
            "children": [stmt.to_tree_dict() for stmt in self.statements]
        }


class LiteralNode(ASTNode):
    def __init__(self, value: Union[str, int], literal_type: str, line: int = 1, column: int = 1):
        super().__init__("Literal", line, column)
        self.value = value
        self.literal_type = literal_type  # 'STRING' or 'NUMBER'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Literal",
            "literal_type": self.literal_type,
            "value": self.value,
            "line": self.line,
            "column": self.column
        }

    def to_tree_dict(self) -> Dict[str, Any]:
        return {
            "name": f"Literal({self.literal_type}): {repr(self.value)}"
        }


class VariableNode(ASTNode):
    def __init__(self, name: str, line: int = 1, column: int = 1):
        super().__init__("Variable", line, column)
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Variable",
            "name": self.name,
            "line": self.line,
            "column": self.column
        }

    def to_tree_dict(self) -> Dict[str, Any]:
        return {
            "name": f"Variable: {self.name}"
        }


class OpenNode(ASTNode):
    def __init__(self, url: ASTNode, line: int = 1, column: int = 1):
        super().__init__("Open", line, column)
        self.url = url  # LiteralNode or VariableNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Open",
            "url": self.url.to_dict(),
            "line": self.line,
            "column": self.column
        }

    def to_tree_dict(self) -> Dict[str, Any]:
        return {
            "name": "Open",
            "children": [self.url.to_tree_dict()]
        }


class GapNode(ASTNode):
    def __init__(self, duration: ASTNode, line: int = 1, column: int = 1):
        super().__init__("Gap", line, column)
        self.duration = duration  # LiteralNode or VariableNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Gap",
            "duration": self.duration.to_dict(),
            "line": self.line,
            "column": self.column
        }

    def to_tree_dict(self) -> Dict[str, Any]:
        return {
            "name": "Gap",
            "children": [self.duration.to_tree_dict()]
        }


class TypeNode(ASTNode):
    def __init__(self, text: ASTNode, line: int = 1, column: int = 1):
        super().__init__("Type", line, column)
        self.text = text  # LiteralNode or VariableNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Type",
            "text": self.text.to_dict(),
            "line": self.line,
            "column": self.column
        }

    def to_tree_dict(self) -> Dict[str, Any]:
        return {
            "name": "Type",
            "children": [self.text.to_tree_dict()]
        }


class PressNode(ASTNode):
    def __init__(self, key: str, count: ASTNode, line: int = 1, column: int = 1):
        super().__init__("Press", line, column)
        self.key = key
        self.count = count  # LiteralNode or VariableNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Press",
            "key": self.key,
            "count": self.count.to_dict(),
            "line": self.line,
            "column": self.column
        }

    def to_tree_dict(self) -> Dict[str, Any]:
        return {
            "name": f"Press ({self.key})",
            "children": [self.count.to_tree_dict()]
        }


class LoopNode(ASTNode):
    def __init__(self, count: ASTNode, body: List[ASTNode], line: int = 1, column: int = 1):
        super().__init__("Loop", line, column)
        self.count = count  # LiteralNode or VariableNode
        self.body = body

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Loop",
            "count": self.count.to_dict(),
            "body": [stmt.to_dict() for stmt in self.body],
            "line": self.line,
            "column": self.column
        }

    def to_tree_dict(self) -> Dict[str, Any]:
        return {
            "name": "Loop",
            "children": [
                {"name": "Count", "children": [self.count.to_tree_dict()]},
                {"name": "Body", "children": [stmt.to_tree_dict() for stmt in self.body]}
            ]
        }


class SetNode(ASTNode):
    def __init__(self, name: str, value: ASTNode, line: int = 1, column: int = 1):
        super().__init__("Set", line, column)
        self.name = name
        self.value = value  # LiteralNode or VariableNode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Set",
            "name": self.name,
            "value": self.value.to_dict(),
            "line": self.line,
            "column": self.column
        }

    def to_tree_dict(self) -> Dict[str, Any]:
        return {
            "name": f"Set ({self.name})",
            "children": [self.value.to_tree_dict()]
        }
