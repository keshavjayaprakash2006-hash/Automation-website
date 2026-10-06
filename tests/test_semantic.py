"""
Unit tests for AutoScript Semantic Analyzer & Symbol Table.
"""

import pytest
from backend.lexer.lexer import Lexer
from backend.parser.parser import Parser
from backend.semantic.analyzer import SemanticAnalyzer
from backend.errors.compiler_errors import CompilerError

def test_semantic_negative_gap():
    code = 'GAP -5'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_code=code)
    ast, _ = parser.parse()

    analyzer = SemanticAnalyzer(ast, source_code=code)
    with pytest.raises(CompilerError) as exc_info:
        analyzer.analyze()
    assert exc_info.value.phase == "SEMANTIC"
    assert "GAP duration must be a positive number" in exc_info.value.message

def test_semantic_unsupported_key():
    code = 'PRESS UNKNOWN_KEY'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_code=code)
    ast, _ = parser.parse()

    analyzer = SemanticAnalyzer(ast, source_code=code)
    with pytest.raises(CompilerError) as exc_info:
        analyzer.analyze()
    assert exc_info.value.phase == "SEMANTIC"
    assert "Unsupported key 'UNKNOWN_KEY'" in exc_info.value.message

def test_semantic_variables():
    code = 'SET DELAY = 5\nGAP DELAY'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_code=code)
    ast, _ = parser.parse()

    analyzer = SemanticAnalyzer(ast, source_code=code)
    sym_table = analyzer.analyze()
    assert sym_table.is_defined("DELAY")
    sym = sym_table.lookup("DELAY")
    assert sym.value == 5
