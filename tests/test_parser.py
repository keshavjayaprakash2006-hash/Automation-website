"""
Unit tests for AutoScript Parser & AST Generation.
"""

import pytest
from backend.lexer.lexer import Lexer
from backend.parser.parser import Parser
from backend.ast.nodes import ProgramNode, OpenNode, LoopNode
from backend.errors.compiler_errors import CompilerError

def test_parser_valid_program():
    code = 'OPEN "https://example.com"\nLOOP 3 {\n    PRESS TAB\n}'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_code=code)
    ast, parse_tree = parser.parse()

    assert isinstance(ast, ProgramNode)
    assert len(ast.statements) == 2
    assert isinstance(ast.statements[0], OpenNode)
    assert isinstance(ast.statements[1], LoopNode)
    assert len(ast.statements[1].body) == 1

def test_parser_missing_brace():
    code = 'LOOP 3 {\n    PRESS TAB'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_code=code)
    with pytest.raises(CompilerError) as exc_info:
        parser.parse()
    assert exc_info.value.phase == "SYNTAX"
    assert "Unmatched '{'" in exc_info.value.message

def test_parser_invalid_command_arg():
    code = 'TYPE 123'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_code=code)
    with pytest.raises(CompilerError) as exc_info:
        parser.parse()
    assert exc_info.value.phase == "SYNTAX"
    assert "TYPE command expects a string" in exc_info.value.message
