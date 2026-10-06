"""
Unit tests for AutoScript IR Generation.
"""

from backend.lexer.lexer import Lexer
from backend.parser.parser import Parser
from backend.semantic.analyzer import SemanticAnalyzer
from backend.ir.ir_generator import IRGenerator

def test_ir_generation():
    code = 'OPEN "https://example.com"\nGAP 3\nPRESS TAB 2'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_code=code)
    ast, _ = parser.parse()
    analyzer = SemanticAnalyzer(ast, source_code=code)
    sym_table = analyzer.analyze()

    ir_gen = IRGenerator(ast, sym_table)
    ir = ir_gen.generate()

    assert len(ir) == 3
    assert ir[0].op == "OPEN_URL" and ir[0].args[0] == "https://example.com"
    assert ir[1].op == "WAIT" and ir[1].args[0] == 3
    assert ir[2].op == "PRESS_KEY" and ir[2].args[0] == "TAB" and ir[2].args[1] == 2
