"""
Unit tests for AutoScript Python Code Generation.
"""

from backend.lexer.lexer import Lexer
from backend.parser.parser import Parser
from backend.ir.ir_generator import IRGenerator
from backend.codegen.python_generator import PythonCodeGenerator

def test_codegen():
    code = 'OPEN "https://example.com"\nLOOP 2 {\n    PRESS TAB\n}'
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, source_code=code)
    ast, _ = parser.parse()
    ir_gen = IRGenerator(ast)
    ir = ir_gen.generate()

    codegen = PythonCodeGenerator(ir)
    py_code = codegen.generate()

    assert "import webbrowser" in py_code
    assert "import pyautogui" in py_code
    assert "webbrowser.open('https://example.com')" in py_code
    assert "for _ in range(2):" in py_code
    assert "pyautogui.press('tab')" in py_code
