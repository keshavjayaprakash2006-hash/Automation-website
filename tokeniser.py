"""
AutoScript Compiler - Lexer Wrapper (Review-1 Backward Compatibility)
Delegates tokenization to backend.lexer module.
"""

from backend.lexer.lexer import Lexer
from backend.errors.compiler_errors import CompilerError

def tokenize_file(filepath):
    try:
        with open(filepath, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{filepath}'")
        return []

    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        return [[t.type.value, t.value] for t in tokens if t.type.value != "EOF"]
    except CompilerError as e:
        print(e)
        return []

if __name__ == "__main__":
    tokenized_output = tokenize_file('sample_file.txt')
    for token in tokenized_output:
        print(token)