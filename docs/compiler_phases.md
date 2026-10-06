# Compiler Phases Explanation

The AutoScript Compiler demonstrates all 10 standard compiler phases:

1. **Lexical Analysis (Lexer)**: Reads raw AutoScript text, handles line numbers, column numbers, skips comments (`#`, `//`), and emits `Token` structures.
2. **Syntax Analysis (Parser)**: Recursive-descent parser verifying grammar structure and constructing the Concrete Parse Tree (CST).
3. **AST Generation**: Converts CST into strongly-typed Abstract Syntax Tree (`ASTNode` hierarchy).
4. **Semantic Analysis**: Checks type compatibility, positive range constraints on numbers, supported key names, and block integrity.
5. **Symbol Table**: Records variable names, data types (`STRING`, `NUMBER`), values, scopes, and line locations.
6. **Intermediate Representation (IR)**: Generates linear instruction-based quadruples (`OPEN_URL`, `WAIT`, `TYPE_TEXT`, `PRESS_KEY`, `LOOP_START`, `LOOP_END`).
7. **Code Generation**: Translates IR into clean, indented Python target code utilizing `webbrowser`, `time`, and `pyautogui`.
8. **Simulation (Mode 1)**: Computes timestamped execution trace logs without modifying mouse or keyboard.
9. **Real Execution (Mode 2)**: Executes generated Python code safely in isolated thread/process with emergency stop.
10. **Error Handling & Diagnostics**: Formats IDE-style diagnostic errors with line, column, and visual caret (`^^^`) snippet output.
