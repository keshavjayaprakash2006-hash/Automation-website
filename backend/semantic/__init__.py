"""AutoScript Compiler Semantic Package."""
from backend.semantic.symbol_table import SymbolTable, Symbol
from backend.semantic.analyzer import SemanticAnalyzer, SUPPORTED_KEYS

__all__ = ["SymbolTable", "Symbol", "SemanticAnalyzer", "SUPPORTED_KEYS"]
