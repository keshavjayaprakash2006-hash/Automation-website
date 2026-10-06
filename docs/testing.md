# AutoScript Testing Strategy

The test suite is built using `pytest` and verifies every stage of the compiler pipeline independently as well as end-to-end.

## Test Suite Components

| File | Tested Component |
|---|---|
| `tests/test_lexer.py` | Tokenization, comments, line/col tracking, unterminated strings, unexpected characters |
| `tests/test_parser.py` | Recursive-descent parsing, AST nodes, parse trees, missing braces, type mismatches |
| `tests/test_semantic.py` | Range checks, negative durations, unsupported keys, symbol table variables |
| `tests/test_ir.py` | Quadruple IR instruction generation, loop opcodes |
| `tests/test_codegen.py` | Target Python code output formatting, imports, pyautogui calls |
| `tests/test_end_to_end.py` | Full compiler pipeline integration on complex login and loop scripts |

## Running Tests
To run all tests:
```powershell
python -m pytest
```
