"""
AutoScript Compiler - Engine & Code Generator (Review-1 Backward Compatibility)
Delegates compilation and execution code generation to the backend compiler pipeline.
"""

from backend.compiler import AutoScriptCompiler

def execute(tokens):
    # Backward compatibility signature: tokens parameter ignored, compiler uses sample_file.txt
    pass

def compile_and_print(filepath):
    try:
        with open(filepath, 'r') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"Error: Could not find '{filepath}'")
        return

    compiler = AutoScriptCompiler(code)
    result = compiler.compile()

    if result["success"]:
        print("--- GENERATED PYTHON CODE ---")
        print(result["generated_code"])
    else:
        print("--- COMPILER ERRORS ---")
        for err in result["errors"]:
            print(err["formatted"])

if __name__ == "__main__":
    compile_and_print('sample_file.txt')