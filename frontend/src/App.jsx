import React, { useState, useEffect } from 'react';
import {
  Play, Cpu, AlertTriangle, Square, Copy, Download, FileCode,
  CheckCircle, XCircle, Terminal, Layers, Table, Code2, FolderOpen, RefreshCw
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8000/api';

const DEFAULT_CODE = `# AutoScript Login Automation Example
OPEN "https://practicetestautomation.com/practice-test-login/"
GAP 5
PRESS TAB 9
TYPE "Student"
PRESS TAB
TYPE "Password123"
PRESS ENTER

LOOP 3 {
    PRESS TAB
}`;

export default function App() {
  const [sourceCode, setSourceCode] = useState(DEFAULT_CODE);
  const [activeTab, setActiveTab] = useState('tokens');
  const [examples, setExamples] = useState({});
  const [selectedExample, setSelectedExample] = useState('login.as');
  const [compileResult, setCompileResult] = useState(null);
  const [simulationLogs, setSimulationLogs] = useState([]);
  const [executionLogs, setExecutionLogs] = useState([]);
  const [isCompiling, setIsCompiling] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [showRunModal, setShowRunModal] = useState(false);
  const [copyNotice, setCopyNotice] = useState(false);

  // Fetch built-in examples on load
  useEffect(() => {
    fetch(`${API_BASE}/examples`)
      .then(res => res.json())
      .then(data => {
        setExamples(data);
      })
      .catch(err => console.error("Failed to load examples:", err));
  }, []);

  // Auto-compile on initial load or code change after brief debounce
  useEffect(() => {
    handleCompile();
  }, []);

  const handleCompile = async () => {
    setIsCompiling(true);
    try {
      const res = await fetch(`${API_BASE}/compile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: sourceCode })
      });
      const data = await res.json();
      setCompileResult(data);
      if (data.errors && data.errors.length > 0) {
        setActiveTab('errors');
      }
    } catch (err) {
      console.error("Compile error:", err);
    } finally {
      setIsCompiling(false);
    }
  };

  const handleSimulate = async () => {
    setIsCompiling(true);
    setActiveTab('execution');
    try {
      const res = await fetch(`${API_BASE}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: sourceCode })
      });
      const data = await res.json();
      setSimulationLogs(data.logs || []);
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setIsCompiling(false);
    }
  };

  const handleRealRun = async () => {
    setShowRunModal(false);
    setIsExecuting(true);
    setActiveTab('execution');
    try {
      const res = await fetch(`${API_BASE}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: sourceCode })
      });
      const data = await res.json();
      setExecutionLogs(data.logs || []);
    } catch (err) {
      console.error("Execution error:", err);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleStop = async () => {
    try {
      await fetch(`${API_BASE}/stop`, { method: 'POST' });
      setExecutionLogs(prev => [...prev, "[USER STOP SIGNAL SENT] Execution interrupted."]);
    } catch (err) {
      console.error("Stop failed:", err);
    }
  };

  const handleSelectExample = (key) => {
    setSelectedExample(key);
    if (examples[key]) {
      setSourceCode(examples[key].code);
    }
  };

  const handleCopyCode = () => {
    if (compileResult?.generated_code) {
      navigator.clipboard.writeText(compileResult.generated_code);
      setCopyNotice(true);
      setTimeout(() => setCopyNotice(false), 2000);
    }
  };

  const handleDownloadPy = () => {
    if (compileResult?.generated_code) {
      const blob = new Blob([compileResult.generated_code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'generated_automation.py';
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const handleDownloadAs = () => {
    const blob = new Blob([sourceCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'script.as';
    a.click();
    URL.revokeObjectURL(url);
  };

  const lines = sourceCode.split('\n');

  const renderTree = (node) => {
    if (!node) return null;
    return (
      <div className="tree-node" key={node.name + Math.random()}>
        <div className="tree-label">{node.name}</div>
        {node.children && node.children.map(child => renderTree(child))}
      </div>
    );
  };

  const pipeline = compileResult?.pipeline || {
    lexer: 'NOT_EXECUTED', parser: 'NOT_EXECUTED', ast: 'NOT_EXECUTED',
    semantic: 'NOT_EXECUTED', symbol_table: 'NOT_EXECUTED', ir: 'NOT_EXECUTED', codegen: 'NOT_EXECUTED'
  };

  return (
    <div className="ide-container">
      {/* Navbar Header */}
      <div className="navbar">
        <div className="brand">
          <div className="brand-icon">AS</div>
          <div className="brand-text">
            <h1>AutoScript Compiler</h1>
            <span>Domain-Specific Automation Language Compiler</span>
          </div>
        </div>

        <div className="toolbar">
          <select
            className="example-select"
            value={selectedExample}
            onChange={(e) => handleSelectExample(e.target.value)}
          >
            {Object.keys(examples).map(key => (
              <option key={key} value={key}>
                📁 Example: {examples[key].title}
              </option>
            ))}
          </select>

          <button className="btn" onClick={() => setSourceCode('')}>
            Clear
          </button>
          <button className="btn" onClick={handleDownloadAs}>
            <Download size={14} /> Download .as
          </button>
          <button className="btn btn-primary" onClick={handleCompile} disabled={isCompiling}>
            <RefreshCw size={14} className={isCompiling ? "spin" : ""} /> Compile
          </button>
          <button className="btn btn-success" onClick={handleSimulate}>
            <Cpu size={14} /> Run Simulation
          </button>
          <button className="btn btn-danger" onClick={() => setShowRunModal(true)}>
            <Play size={14} /> Real Execution
          </button>
        </div>
      </div>

      {/* Compiler Pipeline Header */}
      <div className="pipeline-bar">
        {Object.entries(pipeline).map(([stage, status], idx, arr) => (
          <React.Fragment key={stage}>
            <div className={`pipeline-stage ${status}`}>
              {status === 'SUCCESS' && <CheckCircle size={12} />}
              {status === 'ERROR' && <XCircle size={12} />}
              {stage.replace('_', ' ')}
            </div>
            {idx < arr.length - 1 && <span className="pipeline-arrow">→</span>}
          </React.Fragment>
        ))}
      </div>

      {/* Main Work Area */}
      <div className="main-workarea">
        {/* Code Editor Panel */}
        <div className="editor-panel">
          <div className="panel-header">
            <span>AUTOSCRIPT SOURCE EDITOR (.as)</span>
            <span>{lines.length} Lines</span>
          </div>
          <div className="code-editor-wrapper">
            <div className="line-numbers">
              {lines.map((_, i) => (
                <div key={i}>{i + 1}</div>
              ))}
            </div>
            <textarea
              className="code-textarea"
              value={sourceCode}
              onChange={(e) => setSourceCode(e.target.value)}
              spellCheck="false"
            />
          </div>
        </div>

        {/* Right Inspector Tabs Panel */}
        <div className="inspector-panel">
          <div className="tabs-header">
            <button className={`tab-btn ${activeTab === 'tokens' ? 'active' : ''}`} onClick={() => setActiveTab('tokens')}>
              <Table size={14} /> Tokens ({compileResult?.tokens?.length || 0})
            </button>
            <button className={`tab-btn ${activeTab === 'parsetree' ? 'active' : ''}`} onClick={() => setActiveTab('parsetree')}>
              <Layers size={14} /> Parse Tree
            </button>
            <button className={`tab-btn ${activeTab === 'ast' ? 'active' : ''}`} onClick={() => setActiveTab('ast')}>
              <FileCode size={14} /> AST
            </button>
            <button className={`tab-btn ${activeTab === 'semantic' ? 'active' : ''}`} onClick={() => setActiveTab('semantic')}>
              <CheckCircle size={14} /> Semantic Analysis
            </button>
            <button className={`tab-btn ${activeTab === 'symboltable' ? 'active' : ''}`} onClick={() => setActiveTab('symboltable')}>
              <Table size={14} /> Symbol Table
            </button>
            <button className={`tab-btn ${activeTab === 'ir' ? 'active' : ''}`} onClick={() => setActiveTab('ir')}>
              <Terminal size={14} /> IR
            </button>
            <button className={`tab-btn ${activeTab === 'codegen' ? 'active' : ''}`} onClick={() => setActiveTab('codegen')}>
              <Code2 size={14} /> Python Code
            </button>
            <button className={`tab-btn ${activeTab === 'execution' ? 'active' : ''}`} onClick={() => setActiveTab('execution')}>
              <Play size={14} /> Execution Trace
            </button>
            <button className={`tab-btn ${activeTab === 'errors' ? 'active' : ''}`} onClick={() => setActiveTab('errors')}>
              <AlertTriangle size={14} /> Errors ({compileResult?.errors?.length || 0})
            </button>
          </div>

          <div className="tab-content">
            {/* Tokens Tab */}
            {activeTab === 'tokens' && (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Type</th>
                    <th>Value</th>
                    <th>Line</th>
                    <th>Column</th>
                  </tr>
                </thead>
                <tbody>
                  {compileResult?.tokens?.map((t, idx) => (
                    <tr key={idx}>
                      <td>{idx + 1}</td>
                      <td>
                        <span className={`badge badge-${t.type.toLowerCase()}`}>{t.type}</span>
                      </td>
                      <td><code>{t.value}</code></td>
                      <td>{t.line}</td>
                      <td>{t.column}</td>
                    </tr>
                  ))}
                  {(!compileResult?.tokens || compileResult.tokens.length === 0) && (
                    <tr>
                      <td colSpan="5" style={{ textAlign: 'center', color: '#6b7280' }}>No tokens generated.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}

            {/* Parse Tree Tab */}
            {activeTab === 'parsetree' && (
              <div>
                {compileResult?.parse_tree ? renderTree(compileResult.parse_tree) : <p style={{ color: '#6b7280' }}>No Parse Tree generated.</p>}
              </div>
            )}

            {/* AST Tab */}
            {activeTab === 'ast' && (
              <div>
                {compileResult?.ast ? renderTree(compileResult.ast) : <p style={{ color: '#6b7280' }}>No AST generated.</p>}
              </div>
            )}

            {/* Semantic Analysis Tab */}
            {activeTab === 'semantic' && (
              <div>
                <div style={{ marginBottom: 16 }}>
                  {compileResult?.pipeline?.semantic === 'SUCCESS' ? (
                    <div style={{ color: '#34d399', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                      <CheckCircle size={18} /> Semantic Analysis Passed: All types, positive constraints, keys, and variable scopes are valid.
                    </div>
                  ) : (
                    <div style={{ color: '#fb7185', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                      <XCircle size={18} /> Semantic Analysis Failed. Check Errors tab.
                    </div>
                  )}
                </div>

                <ul style={{ lineHeight: 1.8, fontSize: 13, color: '#9ca3af', marginLeft: 20 }}>
                  <li>✓ GAP duration checks (must be positive number)</li>
                  <li>✓ LOOP iteration checks (must be positive integer)</li>
                  <li>✓ PRESS key validation (must be in supported key set)</li>
                  <li>✓ TYPE text validation (must be string)</li>
                  <li>✓ Variable scope and declaration tracking</li>
                </ul>
              </div>
            )}

            {/* Symbol Table Tab */}
            {activeTab === 'symboltable' && (
              <div>
                {compileResult?.symbol_table?.length > 0 ? (
                  <table className="data-table">
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
                          <td><code>{sym.value}</code></td>
                          <td>{sym.scope}</td>
                          <td>{sym.line}</td>
                          <td>{sym.column}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p style={{ color: '#9ca3af', fontStyle: 'italic' }}>
                    No user-defined symbols in current program. (Use <code>SET VAR = VAL</code> to define variables).
                  </p>
                )}
              </div>
            )}

            {/* IR Tab */}
            {activeTab === 'ir' && (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>OpCode</th>
                    <th>Arguments</th>
                    <th>Line</th>
                    <th>Instruction</th>
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
                    <tr>
                      <td colSpan="5" style={{ textAlign: 'center', color: '#6b7280' }}>No IR generated.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}

            {/* Python Code Tab */}
            {activeTab === 'codegen' && (
              <div>
                <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                  <button className="btn" onClick={handleCopyCode}>
                    <Copy size={14} /> {copyNotice ? "Copied!" : "Copy Python Code"}
                  </button>
                  <button className="btn" onClick={handleDownloadPy}>
                    <Download size={14} /> Download .py File
                  </button>
                </div>
                <div className="console-box" style={{ color: '#38bdf8' }}>
                  {compileResult?.generated_code || "# No Python code generated."}
                </div>
              </div>
            )}

            {/* Execution Tab */}
            {activeTab === 'execution' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <span style={{ fontSize: 13, color: '#9ca3af' }}>Execution Trace Console</span>
                  {isExecuting && (
                    <button className="btn btn-danger" onClick={handleStop}>
                      <Square size={14} /> Emergency Stop
                    </button>
                  )}
                </div>
                <div className="console-box">
                  {simulationLogs.length > 0 && (
                    <div>
                      {simulationLogs.map((log, idx) => (
                        <div key={idx}>{log}</div>
                      ))}
                    </div>
                  )}
                  {executionLogs.length > 0 && (
                    <div style={{ marginTop: 16 }}>
                      {executionLogs.map((log, idx) => (
                        <div key={idx}>{log}</div>
                      ))}
                    </div>
                  )}
                  {simulationLogs.length === 0 && executionLogs.length === 0 && (
                    <div style={{ color: '#6b7280' }}>
                      Click "Run Simulation" or "Real Execution" to view output.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Errors Tab */}
            {activeTab === 'errors' && (
              <div>
                {compileResult?.errors?.length > 0 ? (
                  compileResult.errors.map((err, idx) => (
                    <div key={idx} className="error-diagnostic">
                      <div className="error-header">
                        [{err.phase} ERROR] Line {err.line}, Column {err.column}: {err.message}
                      </div>
                      {err.snippet && (
                        <div className="error-snippet">
                          {err.snippet}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div style={{ color: '#34d399', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <CheckCircle size={18} /> No compilation errors detected!
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Real Execution Confirmation Modal */}
      {showRunModal && (
        <div className="modal-overlay">
          <div className="modal-box">
            <div className="modal-title">⚠️ Real Automation Warning</div>
            <div className="modal-body">
              Real execution will perform active mouse and keyboard controls on your computer using PyAutoGUI.
              <br /><br />
              <strong>Safety Reminder:</strong>
              <ul>
                <li>Save your work before proceeding.</li>
                <li>Move your mouse cursor to any corner of the screen to trigger PyAutoGUI Fail-Safe emergency stop.</li>
              </ul>
            </div>
            <div className="modal-actions">
              <button className="btn" onClick={() => setShowRunModal(false)}>Cancel</button>
              <button className="btn btn-danger" onClick={handleRealRun}>Proceed with Real Automation</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
