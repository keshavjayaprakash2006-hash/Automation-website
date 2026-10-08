/**
 * AutoScript Compiler - Centralized API Service
 * Handles network requests, fallback URL resolution, health checks, and error formatting.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export async function checkHealth() {
  try {
    const res = await fetch(`${BASE_URL}/api/health`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' }
    });
    if (!res.ok) return { online: false, message: `Server responded with status ${res.status}` };
    const data = await res.json();
    return { online: data.status === 'ok', service: data.service };
  } catch (err) {
    return { online: false, message: err.message || 'Failed to fetch' };
  }
}

export async function compileSource(source) {
  try {
    const res = await fetch(`${BASE_URL}/api/compile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source })
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    console.error("Compilation network error:", err);
    return {
      success: false,
      pipeline: {
        lexer: 'ERROR', parser: 'NOT_EXECUTED', ast: 'NOT_EXECUTED',
        semantic: 'NOT_EXECUTED', symbol_table: 'NOT_EXECUTED', ir: 'NOT_EXECUTED', codegen: 'NOT_EXECUTED'
      },
      tokens: [],
      parse_tree: null,
      ast: null,
      semantic: { success: false, errors: [] },
      symbol_table: [],
      ir: [],
      generated_code: '',
      errors: [
        {
          phase: 'NETWORK',
          message: `Backend connection failed (${err.message}). Ensure FastAPI backend is running on ${BASE_URL}.`,
          line: 1,
          column: 1,
          snippet: '',
          formatted: `[NETWORK ERROR]: Could not connect to backend server at ${BASE_URL}`
        }
      ]
    };
  }
}

export async function simulateSource(source) {
  try {
    const res = await fetch(`${BASE_URL}/api/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      success: false,
      logs: [`Simulation failed: ${err.message}. Ensure backend is running on ${BASE_URL}.`]
    };
  }
}

export async function fetchDemos() {
  try {
    const res = await fetch(`${BASE_URL}/api/demos`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch demos:", err);
    return {};
  }
}

export async function runDemo(demoId) {
  try {
    const res = await fetch(`${BASE_URL}/api/demo/${demoId}/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return await res.json();
  } catch (err) {
    return {
      success: false,
      message: `Execution error: ${err.message}`,
      logs: [`Backend unavailable (${err.message}). Start the AutoScript backend on ${BASE_URL}.`]
    };
  }
}

export async function stopExecution() {
  try {
    const res = await fetch(`${BASE_URL}/api/stop`, { method: 'POST' });
    return await res.json();
  } catch (err) {
    return { success: false, message: err.message };
  }
}
