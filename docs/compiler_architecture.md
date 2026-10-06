# AutoScript Compiler Architecture

## 1. Overview
AutoScript is a Domain-Specific Language (DSL) compiler designed to translate human-readable browser and desktop automation commands into executable Python scripts leveraging `webbrowser`, `time`, and `pyautogui`.

The system is structured following classical compiler design principles with a decoupled, modular architecture:

```
                          AutoScript Source (.as)
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Lexical Analyzer│
                            │   (lexer.py)    │
                            └────────┬────────┘
                                     │ Tokens
                                     ▼
                            ┌─────────────────┐
                            │ Recursive-Descent│
                            │     Parser      │
                            │   (parser.py)   │
                            └────────┬────────┘
                                     │ AST & CST
                                     ▼
                            ┌─────────────────┐
                            │Semantic Analyzer│
                            │  (analyzer.py)  │
                            └────────┬────────┘
                                     │ Validated AST & Symbol Table
                                     ▼
                            ┌─────────────────┐
                            │  IR Generator   │
                            │(ir_generator.py)│
                            └────────┬────────┘
                                     │ Linear Quadruple IR
                                     ▼
                            ┌─────────────────┐
                            │ Python CodeGen  │
                            │(python_generator│
                            └────────┬────────┘
                                     │ Executable Python Code
                                     ▼
                       ┌───────────────────────────┐
                       │      Executor Engine      │
                       │ ┌───────────────┬───────┐ │
                       │ │ Simulation    │ Real  │ │
                       │ │ (Trace Logs)  │ Exec  │ │
                       │ └───────────────┴───────┘ │
                       └───────────────────────────┘
```

## 2. Directory Structure

```
COMP_PROJ/
├── backend/
│   ├── ast/
│   │   └── nodes.py          # AST Node Hierarchy
│   ├── codegen/
│   │   └── python_generator.py # Python Target Code Generator
│   ├── errors/
│   │   └── compiler_errors.py  # Diagnostic Error Formatting & Carets
│   ├── executor/
│   │   └── executor.py       # Mode 1 (Simulation) & Mode 2 (Real Exec)
│   ├── ir/
│   │   └── ir_generator.py   # Quadruple/Instruction-based IR
│   ├── lexer/
│   │   ├── token.py          # TokenType Enum & Token Data Structure
│   │   └── lexer.py          # Lexical Analyzer with line/col tracking
│   ├── parser/
│   │   └── parser.py         # Recursive-Descent Parser & CST Generator
│   ├── semantic/
│   │   ├── symbol_table.py   # Symbol Table & Scope Management
│   │   └── analyzer.py       # Semantic Analyzer & Type Checker
│   ├── compiler.py           # Master Pipeline Orchestrator
│   └── main.py               # FastAPI REST Application Server
├── frontend/                 # React + Vite Compiler IDE UI
├── examples/                 # Sample AutoScript Programs (.as)
├── tests/                    # Pytest Unit & Integration Test Suite
├── docs/                     # Compiler Design Documentation
├── requirements.txt          # Python Dependencies
└── README.md                 # Complete Project Manual
```
