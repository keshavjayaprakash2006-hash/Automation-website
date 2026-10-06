"""
End-to-end integration tests for AutoScript Compiler pipeline.
"""

from backend.compiler import AutoScriptCompiler

def test_full_pipeline_login_program():
    code = """OPEN "https://practicetestautomation.com/practice-test-login/"
GAP 5
PRESS TAB 9
TYPE "Student"
PRESS TAB
TYPE "Password123"
PRESS ENTER"""

    compiler = AutoScriptCompiler(code)
    result = compiler.compile()

    assert result["success"] is True
    assert len(result["tokens"]) > 0
    assert result["parse_tree"] is not None
    assert result["ast"] is not None
    assert len(result["ir"]) == 7
    assert "webbrowser.open(" in result["generated_code"]
    assert "pyautogui.write('Student')" in result["generated_code"]
    assert "pyautogui.write('Password123')" in result["generated_code"]
    assert "pyautogui.press('enter')" in result["generated_code"]
    assert len(result["errors"]) == 0
