"""
AutoScript Compiler - Main Compiler Orchestrator
Coordinates Lexer, Parser, AST Generator, Semantic Analyzer, Symbol Table, IR Generator, and Code Generator.
"""

from typing import Dict, Any, List
from backend.lexer.lexer import Lexer
from backend.parser.parser import Parser
from backend.semantic.analyzer import SemanticAnalyzer
from backend.ir.ir_generator import IRGenerator
from backend.codegen.python_generator import PythonCodeGenerator
from backend.errors.compiler_errors import CompilerError

class AutoScriptCompiler:
    def __init__(self, source_code: str):
        self.source_code = source_code

    def compile(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "success": False,
            "pipeline": {
                "lexer": "NOT_EXECUTED",
                "parser": "NOT_EXECUTED",
                "ast": "NOT_EXECUTED",
                "semantic": "NOT_EXECUTED",
                "symbol_table": "NOT_EXECUTED",
                "ir": "NOT_EXECUTED",
                "codegen": "NOT_EXECUTED"
            },
            "tokens": [],
            "parse_tree": None,
            "ast": None,
            "semantic": {
                "success": False,
                "errors": []
            },
            "symbol_table": [],
            "ir": [],
            "generated_code": "",
            "errors": []
        }

        try:
            # Phase 1: Lexical Analysis
            result["pipeline"]["lexer"] = "PROCESSING"
            lexer = Lexer(self.source_code)
            tokens = lexer.tokenize()
            result["tokens"] = [t.to_dict() for t in tokens]
            result["pipeline"]["lexer"] = "SUCCESS"

            # Phase 2 & 3: Syntax Analysis & AST Generation
            result["pipeline"]["parser"] = "PROCESSING"
            result["pipeline"]["ast"] = "PROCESSING"
            parser = Parser(tokens, source_code=self.source_code)
            ast_root, parse_tree = parser.parse()
            result["parse_tree"] = parse_tree
            result["ast"] = ast_root.to_tree_dict()
            result["pipeline"]["parser"] = "SUCCESS"
            result["pipeline"]["ast"] = "SUCCESS"

            # Phase 4 & 5: Semantic Analysis & Symbol Table
            result["pipeline"]["semantic"] = "PROCESSING"
            result["pipeline"]["symbol_table"] = "PROCESSING"
            analyzer = SemanticAnalyzer(ast_root, source_code=self.source_code)
            symbol_table = analyzer.analyze()
            result["symbol_table"] = symbol_table.to_list()
            result["semantic"] = {
                "success": True,
                "errors": []
            }
            result["pipeline"]["semantic"] = "SUCCESS"
            result["pipeline"]["symbol_table"] = "SUCCESS"

            # Phase 6: Intermediate Representation (IR)
            result["pipeline"]["ir"] = "PROCESSING"
            ir_gen = IRGenerator(ast_root, symbol_table=symbol_table)
            ir_instructions = ir_gen.generate()
            result["ir"] = [instr.to_dict() for instr in ir_instructions]
            result["pipeline"]["ir"] = "SUCCESS"

            # Phase 7: Code Generation
            result["pipeline"]["codegen"] = "PROCESSING"
            codegen = PythonCodeGenerator(ir_instructions)
            generated_python = codegen.generate()
            result["generated_code"] = generated_python
            result["pipeline"]["codegen"] = "SUCCESS"

            result["success"] = True

        except CompilerError as e:
            phase_key = e.phase.lower()
            if phase_key in result["pipeline"]:
                result["pipeline"][phase_key] = "ERROR"
            err_dict = e.to_dict()
            result["errors"].append(err_dict)
            if phase_key == "semantic":
                result["semantic"] = {
                    "success": False,
                    "errors": [err_dict]
                }
            result["success"] = False

        except Exception as e:
            err_dict = {
                "phase": "INTERNAL",
                "message": f"Internal compiler error: {str(e)}",
                "line": 1,
                "column": 1,
                "snippet": "",
                "formatted": f"[INTERNAL ERROR]: {str(e)}"
            }
            result["errors"].append(err_dict)
            result["success"] = False

        return result
