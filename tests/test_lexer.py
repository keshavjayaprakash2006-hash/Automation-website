"""
Unit tests for AutoScript Lexical Analyzer (Lexer).
"""

import pytest
from backend.lexer.lexer import Lexer
from backend.lexer.token import TokenType
from backend.errors.compiler_errors import CompilerError

def test_lexer_valid_tokens():
    code = 'OPEN "https://example.com"\nGAP 5\nPRESS TAB 3'
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    # Filter out NEWLINE and EOF
    meaningful = [t for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)]

    assert len(meaningful) == 7
    assert meaningful[0].type == TokenType.COMMAND and meaningful[0].value == "OPEN"
    assert meaningful[1].type == TokenType.STRING and meaningful[1].value == "https://example.com"
    assert meaningful[2].type == TokenType.COMMAND and meaningful[2].value == "GAP"
    assert meaningful[3].type == TokenType.NUMBER and meaningful[3].value == 5
    assert meaningful[4].type == TokenType.COMMAND and meaningful[4].value == "PRESS"
    assert meaningful[5].type == TokenType.KEY and meaningful[5].value == "TAB"
    assert meaningful[6].type == TokenType.NUMBER and meaningful[6].value == 3

def test_lexer_comments():
    code = "# Comment line\nOPEN \"url\" // inline comment"
    lexer = Lexer(code)
    tokens = [t for t in lexer.tokenize() if t.type not in (TokenType.NEWLINE, TokenType.EOF)]
    assert len(tokens) == 2
    assert tokens[0].value == "OPEN"
    assert tokens[1].value == "url"

def test_lexer_unterminated_string():
    code = 'TYPE "unterminated'
    lexer = Lexer(code)
    with pytest.raises(CompilerError) as exc_info:
        lexer.tokenize()
    assert exc_info.value.phase == "LEXICAL"
    assert "Unterminated string" in exc_info.value.message

def test_lexer_unexpected_char():
    code = "OPEN @url"
    lexer = Lexer(code)
    with pytest.raises(CompilerError) as exc_info:
        lexer.tokenize()
    assert exc_info.value.phase == "LEXICAL"
    assert "Unexpected character '@'" in exc_info.value.message
