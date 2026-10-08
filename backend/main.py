"""
AutoScript Compiler - FastAPI Backend Application
Exposes RESTful APIs for compilation, simulation, demo execution, emergency stop, and health status.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from backend.compiler import AutoScriptCompiler
from backend.executor.executor import Executor
from backend.ir.ir_generator import IRGenerator
from backend.parser.parser import Parser
from backend.lexer.lexer import Lexer
from backend.semantic.analyzer import SemanticAnalyzer

app = FastAPI(
    title="AutoScript Compiler API",
    description="REST API for the AutoScript Domain-Specific Automation Language Compiler",
    version="1.0.0"
)

# Enable CORS for frontend integration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompileRequest(BaseModel):
    source: str

DEMOS: Dict[str, Dict[str, Any]] = {
    "login": {
        "id": "login",
        "title": "Login Form Automation",
        "description": "Opens practice login page, waits 5s, tabs to fields, types credentials, and submits form.",
        "code": """# AutoScript Login Automation Example
OPEN "https://practicetestautomation.com/practice-test-login/"
GAP 5
PRESS TAB 9
TYPE "Student"
PRESS TAB
TYPE "Password123"
PRESS ENTER"""
    },
    "form": {
        "id": "form",
        "title": "Form Navigation",
        "description": "Navigates keyboard focus and enters inputs across form controls using GAP and PRESS commands.",
        "code": """# AutoScript Form Navigation Example
OPEN "https://practicetestautomation.com/practice-test-login/"
GAP 3
PRESS TAB 9
TYPE "Student"
PRESS TAB
TYPE "Password123"
"""
    },
    "loop": {
        "id": "loop",
        "title": "Loop Automation",
        "description": "Demonstrates repetitive navigation operations using the AutoScript LOOP construct.",
        "code": """# AutoScript Loop Automation Example
OPEN "https://example.com"
GAP 2

LOOP 3 {
    PRESS TAB
    GAP 1
}"""
    }
}

EXAMPLES: Dict[str, Dict[str, str]] = {
    "login.as": {
        "title": "Login Automation",
        "description": DEMOS["login"]["description"],
        "code": DEMOS["login"]["code"]
    },
    "loop_example.as": {
        "title": "Loop Automation",
        "description": DEMOS["loop"]["description"],
        "code": DEMOS["loop"]["code"]
    },
    "variables.as": {
        "title": "Variables Extension",
        "description": "Demonstrates SET variable declarations and symbol table tracking.",
        "code": """# Variable Declaration & Use
SET WAIT_TIME = 3
SET USER_NAME = "Student"

OPEN "https://example.com"
GAP WAIT_TIME
TYPE USER_NAME
PRESS ENTER"""
    }
}

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AutoScript Compiler API",
        "version": "1.0.0"
    }

@app.get("/api/health")
def get_health():
    return {
        "status": "ok",
        "service": "AutoScript Compiler"
    }

@app.post("/api/compile")
def compile_code(req: CompileRequest):
    compiler = AutoScriptCompiler(req.source)
    return compiler.compile()

@app.post("/api/simulate")
def simulate_code(req: CompileRequest):
    compiler = AutoScriptCompiler(req.source)
    comp_result = compiler.compile()

    if not comp_result["success"]:
        return {
            "success": False,
            "errors": comp_result["errors"],
            "logs": ["Simulation aborted due to compilation errors."]
        }

    lexer = Lexer(req.source)
    tokens = lexer.tokenize()
    parser = Parser(tokens, req.source)
    ast_root, _ = parser.parse()
    analyzer = SemanticAnalyzer(ast_root, req.source)
    symbol_table = analyzer.analyze()
    ir_gen = IRGenerator(ast_root, symbol_table=symbol_table)
    ir_instructions = ir_gen.generate()

    trace = Executor.simulate(ir_instructions)
    return {
        "success": True,
        "errors": [],
        "logs": trace
    }

@app.get("/api/demos")
def get_demos():
    return DEMOS

@app.get("/api/examples")
def get_examples():
    return EXAMPLES

@app.post("/api/demo/{demo_id}/run")
def run_demo(demo_id: str):
    if demo_id not in DEMOS:
        raise HTTPException(status_code=404, detail=f"Demo '{demo_id}' not found. Available demos: {list(DEMOS.keys())}")

    demo_code = DEMOS[demo_id]["code"]
    compiler = AutoScriptCompiler(demo_code)
    comp_result = compiler.compile()

    if not comp_result["success"]:
        return {
            "success": False,
            "demo_id": demo_id,
            "errors": comp_result["errors"],
            "message": "Demo execution aborted due to compiler errors.",
            "logs": []
        }

    lexer = Lexer(demo_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens, demo_code)
    ast_root, _ = parser.parse()
    analyzer = SemanticAnalyzer(ast_root, demo_code)
    symbol_table = analyzer.analyze()
    ir_gen = IRGenerator(ast_root, symbol_table=symbol_table)
    ir_instructions = ir_gen.generate()

    exec_result = Executor.run_real_ir(ir_instructions)
    return {
        "success": exec_result["success"],
        "demo_id": demo_id,
        "message": exec_result["message"],
        "generated_code": comp_result["generated_code"],
        "logs": exec_result["logs"]
    }

@app.post("/api/stop")
def stop_code():
    return Executor.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
