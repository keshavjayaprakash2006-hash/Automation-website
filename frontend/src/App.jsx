import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  CheckCircle, XCircle, Play, Cpu, AlertTriangle, FileCode,
  Layers, Table, Terminal, Code2, BookOpen, ShieldAlert,
  Clock, RefreshCw, X, Server
} from 'lucide-react';
import { checkHealth, compileSource, simulateSource, fetchDemos, runDemo } from './api';

const SAMPLE_PROGRAMS = {
  login: {
    name: 'Login Automation',
    code: `# AutoScript Login Automation Example
OPEN "https://practicetestautomation.com/practice-test-login/"
GAP 5
PRESS TAB 9
TYPE "Student"
PRESS TAB
TYPE "Password123"
PRESS ENTER`
  },
  loop: {
    name: 'Loop Automation',
    code: `# AutoScript Loop Automation Example
OPEN "https://example.com"
GAP 2

LOOP 3 {
    PRESS TAB
    GAP 1
}`
  },
  variables: {
    name: 'Variables Extension',
    code: `# AutoScript Variable Declaration & Usage
SET WAIT_TIME = 3
SET USER_NAME = "Student"

OPEN "https://example.com"
GAP WAIT_TIME
TYPE USER_NAME
PRESS ENTER`
  }
};

const PHASE_DEFS = [
  {
    key: 'lexer',
    num: '01',
    name: 'LEXICAL ANALYSIS',
    shortName: 'Lexer',
    description: 'Scans raw AutoScript code and emits structured Tokens with line and column tracking.'
  },
  {
    key: 'parser',
    num: '02',
    name: 'SYNTAX ANALYSIS',
    shortName: 'Parser',
    description: 'Validates language grammar using recursive descent parsing and constructs the Concrete Parse Tree.'
  },
  {
    key: 'ast',
    num: '03',
    name: 'AST CONSTRUCTION',
    shortName: 'AST',
    description: 'Builds Abstract Syntax Tree hierarchy preserving operation nodes and statement relationships.'
  },
  {
    key: 'semantic',
    num: '04',
    name: 'SEMANTIC ANALYSIS',
    shortName: 'Semantic',
    description: 'Enforces type safety, positive number constraints, supported key sets, and scope rules.'
  },
  {
    key: 'symbol_table',
    num: '05',
    name: 'SYMBOL TABLE',
    shortName: 'Symbol Table',
    description: 'Dynamically manages variable declarations, data types, values, scopes, and source locations.'
  },
  {
    key: 'ir',
    num: '06',
    name: 'INTERMEDIATE REPRESENTATION',
    shortName: 'IR',
    description: 'Translates validated AST into target-independent instruction quadruples.'
  },
  {
    key: 'codegen',
    num: '07',
    name: 'CODE GENERATION',
    shortName: 'Code Gen',
    description: 'Translates IR instructions into clean Python target code using webbrowser, time, and PyAutoGUI.'
  }
];

export default function App() {
  const [sourceCode, setSourceCode] = useState(SAMPLE_PROGRAMS.login.code);
  const [activePhase, setActivePhase] = useState('lexer');
  const [compileResult, setCompileResult] = useState(null);
  const [isCompiling, setIsCompiling] = useState(false);
  const [backendOnline, setBackendOnline] = useState(true);
  const [demos, setDemos] = useState({});
  const [activeDemoModal, setActiveDemoModal] = useState(null);
  const [isRunningDemo, setIsRunningDemo] = useState(false);
  const [demoLogs, setDemoLogs] = useState([]);
  const [traceModal, setTraceModal] = useState(null);
  const [traceLogs, setTraceLogs] = useState([]);

  const debounceTimer = useRef(null);

  useEffect(() => {
    let mounted = true;
    checkHealth().then(health => {
      if (mounted) setBackendOnline(health.online);
    });
    fetchDemos().then(data => {
      if (mounted) setDemos(data);
    });
    const interval = setInterval(async () => {
      const health = await checkHealth();
      if (mounted) setBackendOnline(health.online);
    }, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const runCompilation = useCallback(async (codeToCompile) => {
    setIsCompiling(true);
    const data = await compileSource(codeToCompile);
    setCompileResult(data);

    if (data.errors && data.errors.length > 0) {
      const errPhase = data.errors[0].phase?.toLowerCase();
      if (errPhase && PHASE_DEFS.some(p => p.key === errPhase)) {
        setActivePhase(errPhase);
      }
    }
    setIsCompiling(false);
  }, []);

  // Automatic compilation on source code changes with 500ms debounce
  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(() => {
      runCompilation(sourceCode);
    }, 500);

    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [sourceCode, runCompilation]);

  const handleSelectPreset = (key) => {
    if (SAMPLE_PROGRAMS[key]) {
      setSourceCode(SAMPLE_PROGRAMS[key].code);
    }
  };

  const handleRunDemoConfirm = async (demoId) => {
    setActiveDemoModal(null);
    setIsRunningDemo(true);
    setDemoLogs(["Initiating controlled demo execution..."]);
    const res = await runDemo(demoId);
    setDemoLogs(res.logs || [res.message]);
    setIsRunningDemo(false);
  };

  const handleViewTrace = async (code) => {
    setTraceLogs(["Generating simulation trace..."]);
    setTraceModal(true);
    const res = await simulateSource(code);
    setTraceLogs(res.logs || []);
  };

  const pipeline = compileResult?.pipeline || {
    lexer: 'NOT_EXECUTED', parser: 'NOT_EXECUTED', ast: 'NOT_EXECUTED',
    semantic: 'NOT_EXECUTED', symbol_table: 'NOT_EXECUTED', ir: 'NOT_EXECUTED', codegen: 'NOT_EXECUTED'
  };

  const renderTree = (node, path = 'root') => {
    if (!node) return null;
    return (
      <div className="tree-node" key={path}>
        <div className="tree-label">{node.name}</div>
        {node.children && node.children.map((child, idx) => renderTree(child, `${path}-${idx}`))}
      </div>
    );
  };

  const lineCount = sourceCode.split('\n').length;

  return (
    <div className="app-container">
      {/* 1. Header */}
      <header className="header">
        <div className="header-brand">
          <div className="brand-logo">AS</div>
          <div className="brand-info">
            <h1>AutoScript Compiler</h1>
            <span>Domain-Specific Automation Language Compiler</span>
          </div>
        </div>

        <div className="header-status">
          <div className={`backend-indicator ${backendOnline ? 'online' : 'offline'}`}>
            <span className="dot">●</span>
            <span className="status-label">
              {backendOnline ? 'Compiler Backend Connected' : 'Backend Offline — Start on port 8000'}
            </span>
          </div>
          <div className="header-badge">
            <span>COMPILER DESIGN ACADEMIC PROJECT</span>
          </div>
        </div>
      </header>

      {/* Main Content Scroll Area */}
      <div className="content-scroll">
        {/* 2. Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <h2 className="hero-title">AutoScript Compiler Architecture</h2>
            <p className="hero-subtitle">
              A 10-phase domain-specific language compiler that transforms high-level AutoScript automation program statements into validated intermediate representations and executable target code.
            </p>

            {/* Architecture Visual Pipeline Bar */}
            <div className="hero-pipeline">
              <div className="pipeline-flow">
                <span className="flow-step source">SOURCE</span>
                {PHASE_DEFS.map((phase) => {
                  const status = pipeline[phase.key] || 'NOT_EXECUTED';
                  return (
                    <React.Fragment key={phase.key}>
                      <span className="flow-arrow">→</span>
                      <button
                        className={`flow-step ${phase.key} ${status} ${activePhase === phase.key ? 'active' : ''}`}
                        onClick={() => setActivePhase(phase.key)}
                      >
                        {status === 'SUCCESS' && <CheckCircle size={10} className="status-icon" />}
                        {status === 'ERROR' && <XCircle size={10} className="status-icon" />}
                        {phase.shortName}
                      </button>
                    </React.Fragment>
                  );
                })}
                <span className="flow-arrow">→</span>
                <span className="flow-step exec">EXECUTION</span>
              </div>
            </div>
          </div>
        </section>

        {/* 3. Compiler Architecture Interactive Cards */}
        <section className="architecture-section">
          <div className="section-header">
            <h3>Compiler Pipeline Stages</h3>
            <span className="section-hint">Click any stage card to inspect live output</span>
          </div>

          <div className="architecture-grid">
            {PHASE_DEFS.map((phase) => {
              const status = pipeline[phase.key] || 'NOT_EXECUTED';
              const isSelected = activePhase === phase.key;

              return (
                <div
                  key={phase.key}
                  className={`phase-card ${status} ${isSelected ? 'selected' : ''}`}
                  onClick={() => setActivePhase(phase.key)}
                >
                  <div className="card-top">
                    <span className="phase-num">{phase.num}</span>
                    <span className={`phase-badge badge-${status}`}>
                      {status === 'SUCCESS' && '✓ VALID'}
                      {status === 'ERROR' && '✕ ERROR'}
                      {status === 'NOT_EXECUTED' && '○ PENDING'}
                      {status === 'PROCESSING' && '... RUN'}
                    </span>
                  </div>
                  <h4 className="phase-name">{phase.name}</h4>
                  <p className="phase-desc">{phase.description}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* 4. Try AutoScript Editor Section */}
        <section className="editor-section">
          <div className="editor-card">
            <div className="editor-card-header">
              <div className="editor-title">
                <FileCode size={16} />
                <span>Try AutoScript Source Code</span>
              </div>

              <div className="preset-buttons">
                <span className="preset-label">Load Example:</span>
                <button className="preset-btn" onClick={() => handleSelectPreset('login')}>Login</button>
                <button className="preset-btn" onClick={() => handleSelectPreset('loop')}>Loop</button>
                <button className="preset-btn" onClick={() => handleSelectPreset('variables')}>Variables</button>
              </div>
            </div>

            <div className="editor-body">
              <div className="line-numbers">
                {Array.from({ length: lineCount }, (_, i) => (
                  <div key={i + 1}>{i + 1}</div>
                ))}
              </div>
              <textarea
                className="source-editor"
                value={sourceCode}
                onChange={(e) => setSourceCode(e.target.value)}
                spellCheck="false"
                placeholder="Type AutoScript code here..."
              />
            </div>

            <div className="editor-status-bar">
              <div className="status-indicator">
                {isCompiling ? (
                  <span className="compiling-text">
                    <RefreshCw size={13} className="spin" /> Recompiling AutoScript...
                  </span>
                ) : !backendOnline ? (
                  <span className="error-text">
                    <Server size={14} /> Backend unavailable — Start FastAPI backend on port 8000
                  </span>
                ) : compileResult?.success ? (
                  <span className="success-text">
                    <CheckCircle size={14} /> Compilation successful across all 7 compiler phases
                  </span>
                ) : (
                  <span className="error-text">
                    <XCircle size={14} /> Compilation error detected during {compileResult?.errors?.[0]?.phase || 'processing'}
                  </span>
                )}
              </div>
              <span className="line-info">{lineCount} lines • Auto-compiled</span>
            </div>
          </div>
        </section>

        {/* 5. Dynamic Compiler Output Inspector */}
        <section className="inspector-section">
          <div className="inspector-card">
            <div className="inspector-header">
              <div className="inspector-title">
                <Terminal size={16} />
                <span>Compiler Phase Inspection Output</span>
              </div>

              {/* Horizontal Phase Selector */}
              <div className="phase-tabs">
                {PHASE_DEFS.map((p) => (
                  <button
                    key={p.key}
                    className={`phase-tab ${activePhase === p.key ? 'active' : ''}`}
                    onClick={() => setActivePhase(p.key)}
                  >
                    {p.shortName}
                  </button>
                ))}
              </div>
            </div>

            <div className="inspector-body">
              {/* Errors Display if compilation failed */}
              {compileResult?.errors?.length > 0 && (
                <div className="error-banner">
                  {compileResult.errors.map((err, idx) => (
                    <div key={idx} className="error-box">
                      <div className="error-box-header">
                        <AlertTriangle size={15} />
                        <span>[{err.phase} ERROR] Line {err.line}, Column {err.column}: {err.message}</span>
                      </div>
                      {err.snippet && (
                        <pre className="error-box-snippet">{err.snippet}</pre>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* LEXER OUTPUT */}
              {activePhase === 'lexer' && (
                <div className="output-view">
                  <div className="view-intro">
                    <BookOpen size={14} />
                    <span>Tokens emitted by Lexical Analyzer ({compileResult?.tokens?.length || 0} tokens generated):</span>
                  </div>
                  <div className="table-wrapper">
                    <table className="compiler-table">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>Token Type</th>
                          <th>Value</th>
                          <th>Line</th>
                          <th>Column</th>
                        </tr>
                      </thead>
                      <tbody>
                        {compileResult?.tokens?.map((t, idx) => (
                          <tr key={idx}>
                            <td>{idx + 1}</td>
                            <td><span className={`badge badge-${t.type.toLowerCase()}`}>{t.type}</span></td>
                            <td><code>{t.value}</code></td>
                            <td>{t.line}</td>
                            <td>{t.column}</td>
                          </tr>
                        ))}
                        {(!compileResult?.tokens || compileResult.tokens.length === 0) && (
                          <tr><td colSpan="5" className="empty-cell">No tokens generated.</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* PARSER OUTPUT */}
              {activePhase === 'parser' && (
                <div className="output-view">
                  <div className="view-intro">
                    <Layers size={14} />
                    <span>Concrete Parse Tree generated by Recursive-Descent Parser:</span>
                  </div>
                  <div className="tree-container">
                    {compileResult?.parse_tree ? renderTree(compileResult.parse_tree) : <p className="empty-text">No Parse Tree generated.</p>}
                  </div>
                </div>
              )}

              {/* AST OUTPUT */}
              {activePhase === 'ast' && (
                <div className="output-view">
                  <div className="view-intro">
                    <FileCode size={14} />
                    <span>Abstract Syntax Tree (AST) node hierarchy:</span>
                  </div>
                  <div className="tree-container">
                    {compileResult?.ast ? renderTree(compileResult.ast) : <p className="empty-text">No AST generated.</p>}
                  </div>
                </div>
              )}

              {/* SEMANTIC ANALYSIS OUTPUT */}
              {activePhase === 'semantic' && (
                <div className="output-view">
                  <div className="view-intro">
                    <CheckCircle size={14} />
                    <span>Semantic Analysis Verification Report:</span>
                  </div>
                  <div className="semantic-card">
                    {compileResult?.pipeline?.semantic === 'SUCCESS' ? (
                      <div className="semantic-success">
                        <CheckCircle size={20} />
                        <div>
                          <strong>Semantic Analysis Passed Cleanly</strong>
                          <p>All statement constraints, GAP numeric durations (&gt;0), PRESS supported keys, TYPE string values, and variable identifiers were successfully verified.</p>
                        </div>
                      </div>
                    ) : (
                      <div className="semantic-fail">
                        <XCircle size={20} />
                        <div>
                          <strong>Semantic Validation Failed</strong>
                          <p>Semantic rules violated. Inspect error diagnostic above for exact location.</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* SYMBOL TABLE OUTPUT */}
              {activePhase === 'symbol_table' && (
                <div className="output-view">
                  <div className="view-intro">
                    <Table size={14} />
                    <span>Symbol Table tracking active variable scope declarations:</span>
                  </div>
                  <div className="table-wrapper">
                    {compileResult?.symbol_table?.length > 0 ? (
                      <table className="compiler-table">
                        <thead>
                          <tr>
                            <th>Identifier</th>
                            <th>Type</th>
                            <th>Value</th>
                            <th>Scope</th>
                            <th>Line</th>
                            <th>Column</th>
                          </tr>
                        </thead>
                        <tbody>
                          {compileResult.symbol_table.map((sym, idx) => (
                            <tr key={idx}>
                              <td><strong>{sym.name}</strong></td>
                              <td><span className="badge badge-identifier">{sym.type}</span></td>
                              <td><code>{reprValue(sym.value)}</code></td>
                              <td>{sym.scope}</td>
                              <td>{sym.line}</td>
                              <td>{sym.column}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <p className="empty-text">No user-defined variable symbols in current program. (Use <code>SET VAR = VAL</code> to define variables).</p>
                    )}
                  </div>
                </div>
              )}

              {/* IR OUTPUT */}
              {activePhase === 'ir' && (
                <div className="output-view">
                  <div className="view-intro">
                    <Terminal size={14} />
                    <span>Quadruple/Instruction-based Intermediate Representation (IR):</span>
                  </div>
                  <div className="table-wrapper">
                    <table className="compiler-table">
                      <thead>
                        <tr>
                          <th>#</th>
                          <th>OpCode</th>
                          <th>Arguments</th>
                          <th>Source Line</th>
                          <th>IR Instruction</th>
                        </tr>
                      </thead>
                      <tbody>
                        {compileResult?.ir?.map((instr, idx) => (
                          <tr key={idx}>
                            <td>{instr.index}</td>
                            <td><span className="badge badge-command">{instr.op}</span></td>
                            <td><code>{JSON.stringify(instr.args)}</code></td>
                            <td>{instr.line}</td>
                            <td><code>{instr.instruction}</code></td>
                          </tr>
                        ))}
                        {(!compileResult?.ir || compileResult.ir.length === 0) && (
                          <tr><td colSpan="5" className="empty-cell">No IR instructions generated.</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* CODE GENERATION OUTPUT */}
              {activePhase === 'codegen' && (
                <div className="output-view">
                  <div className="view-intro">
                    <Code2 size={14} />
                    <span>Target Python Code generated dynamically from IR:</span>
                  </div>
                  <pre className="code-block">
                    {compileResult?.generated_code || "# No Python code generated."}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* 6. Real Automation Demos Section */}
        <section className="demos-section">
          <div className="section-header">
            <h3>Real Automation Demonstrations</h3>
            <span className="section-hint">Controlled execution of verified domain-specific automation routines</span>
          </div>

          <div className="demos-grid">
            {/* Demo 1: Login */}
            <div className="demo-card">
              <div className="demo-card-header">
                <span className="demo-tag">DEMO 01</span>
                <h4>Login Form Automation</h4>
              </div>
              <p className="demo-desc">
                Opens practice login page, waits for page load, navigates username/password fields using TAB key, and submits credentials.
              </p>
              <div className="demo-actions">
                <button
                  className="btn btn-primary"
                  onClick={() => setActiveDemoModal('login')}
                  disabled={isRunningDemo || !backendOnline}
                >
                  <Play size={13} /> RUN DEMO
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleViewTrace(SAMPLE_PROGRAMS.login.code)}
                >
                  <Clock size={13} /> VIEW TRACE
                </button>
              </div>
            </div>

            {/* Demo 2: Form Navigation */}
            <div className="demo-card">
              <div className="demo-card-header">
                <span className="demo-tag">DEMO 02</span>
                <h4>Form Navigation</h4>
              </div>
              <p className="demo-desc">
                Demonstrates element focus sequence, timed GAP delays, and string input entering across input controls.
              </p>
              <div className="demo-actions">
                <button
                  className="btn btn-primary"
                  onClick={() => setActiveDemoModal('form')}
                  disabled={isRunningDemo || !backendOnline}
                >
                  <Play size={13} /> RUN DEMO
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleViewTrace(demos.form?.code || SAMPLE_PROGRAMS.login.code)}
                >
                  <Clock size={13} /> VIEW TRACE
                </button>
              </div>
            </div>

            {/* Demo 3: Loop Automation */}
            <div className="demo-card">
              <div className="demo-card-header">
                <span className="demo-tag">DEMO 03</span>
                <h4>Loop Automation</h4>
              </div>
              <p className="demo-desc">
                Demonstrates high-level LOOP iteration statement compilation and repetitive keyboard macro sequence execution.
              </p>
              <div className="demo-actions">
                <button
                  className="btn btn-primary"
                  onClick={() => setActiveDemoModal('loop')}
                  disabled={isRunningDemo || !backendOnline}
                >
                  <Play size={13} /> RUN DEMO
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleViewTrace(SAMPLE_PROGRAMS.loop.code)}
                >
                  <Clock size={13} /> VIEW TRACE
                </button>
              </div>
            </div>
          </div>

          {/* Demo Execution Logs Display */}
          {demoLogs.length > 0 && (
            <div className="demo-logs-card">
              <div className="logs-header">
                <Terminal size={14} />
                <span>Demo Real Execution Logs</span>
              </div>
              <div className="logs-body">
                {demoLogs.map((log, i) => (
                  <div key={i} className="log-line">{log}</div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* 7. Footer / Technology Summary */}
        <footer className="footer">
          <div className="footer-content">
            <p><strong>AutoScript Compiler</strong> — Academic Compiler Design Project</p>
            <p className="footer-tech">
              Lexer • Parser • AST • Semantic Analysis • Symbol Table • Intermediate Representation • Code Generation • Execution Engine
            </p>
          </div>
        </footer>
      </div>

      {/* Confirmation Modal for Running Real Demo */}
      {activeDemoModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog">
            <div className="modal-header">
              <ShieldAlert size={20} color="#f43f5e" />
              <h3>Confirm Real Automation Demo</h3>
              <button className="modal-close" onClick={() => setActiveDemoModal(null)}>
                <X size={16} />
              </button>
            </div>
            <div className="modal-body">
              <p>This demo will execute actual mouse and keyboard controls on your computer using <strong>PyAutoGUI</strong> and open a browser window.</p>
              <div className="warning-box">
                <strong>Safety Fail-Safe:</strong> Move your mouse cursor to any corner of the screen at any time to immediately interrupt PyAutoGUI execution.
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setActiveDemoModal(null)}>
                Cancel
              </button>
              <button
                className="btn btn-danger"
                onClick={() => handleRunDemoConfirm(activeDemoModal)}
              >
                Proceed with Demo Execution
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Simulation Trace Modal */}
      {traceModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog large">
            <div className="modal-header">
              <Cpu size={20} color="#38bdf8" />
              <h3>Safe Simulation Trace (Mode 1)</h3>
              <button className="modal-close" onClick={() => setTraceModal(false)}>
                <X size={16} />
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-desc">Simulation mode generates a step-by-step execution trace without affecting your system controls or opening windows.</p>
              <div className="logs-body trace-console">
                {traceLogs.map((log, i) => (
                  <div key={i} className="log-line">{log}</div>
                ))}
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-primary" onClick={() => setTraceModal(false)}>
                Close Trace
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function reprValue(val) {
  if (val === null || val === undefined) return 'null';
  if (typeof val === 'string') return `"${val}"`;
  return String(val);
}
