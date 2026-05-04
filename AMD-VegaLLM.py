#!/usr/bin/env python3
"""
Vega56 LLM Launcher
-------------------
Entwickelt von bagueDEV
GitHub: https://github.com/bagueDEV
"""
import http.server
import json
import os
import subprocess
import threading
import webbrowser
from pathlib import Path

# ── Konfiguration ─────────────────────────────────────────────
LLAMA_CPP_DIR = str(Path.home() / "llama.cpp")
LLAMA_SERVER = str(Path.home() / "llama.cpp/build/bin/llama-server")
EGPU_ALIVE_BIN = str(Path.home() / "egpu-alive")
DEFAULT_MODELS = "/AI_Models"
LAUNCHER_PORT = 9999
SERVER_PORT = 8080
# ──────────────────────────────────────────────────────────────

server_process = None
egpu_process = None
models_dirs = [DEFAULT_MODELS]

# ─────────────────────────────────────────────────────────────────────────────
# HTML LAUNCHER
# ─────────────────────────────────────────────────────────────────────────────

HTML_LAUNCHER = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Vega56/64 Launcher</title>
<style>
  :root {
    --bg:#0a0a0f;--surface:#111118;--border:#1e1e2e;
    --accent:#ff6b35;--accent2:#e040fb;--text:#e8e8f0;
    --muted:#555570;--green:#00e5a0;--red:#ff4757;
    --mono:ui-monospace,'SF Mono','Menlo','Courier New',monospace;
    --sans:-apple-system,BlinkMacSystemFont,'Helvetica Neue',sans-serif;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--bg);color:var(--text);font-family:var(--mono);
       min-height:100vh;display:flex;flex-direction:column;align-items:center;
       padding:40px 20px;}
  h1{font-family:var(--sans);font-size:1.6rem;font-weight:800;
     color:var(--accent);margin-bottom:4px;letter-spacing:-0.02em;}
  h1 span{color:var(--text);}
  .sub{font-size:0.7rem;color:var(--muted);margin-bottom:32px;letter-spacing:0.08em;text-transform:uppercase;}
  .card{background:var(--surface);border:1px solid var(--border);border-radius:10px;
        padding:24px;width:100%;max-width:640px;margin-bottom:16px;}
  .section-title{font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;
                 color:var(--muted);margin-bottom:12px;}

  /* eGPU Panel */
  .egpu-panel{display:flex;align-items:center;gap:12px;padding:12px 16px;
              background:var(--bg);border:1px solid var(--border);border-radius:8px;margin-bottom:0;}
  .egpu-dot{width:10px;height:10px;border-radius:50%;background:var(--muted);flex-shrink:0;transition:background .3s;}
  .egpu-dot.running{background:var(--green);box-shadow:0 0 8px var(--green);}
  .egpu-dot.error{background:var(--red);box-shadow:0 0 6px var(--red);}
  .egpu-label{font-size:0.75rem;flex:1;color:var(--muted);}
  .egpu-label.running{color:var(--green);}
  .btn-egpu-start{background:var(--green);color:#000;border:none;border-radius:5px;
                  padding:6px 14px;font-family:var(--sans);font-weight:700;font-size:0.72rem;
                  cursor:pointer;white-space:nowrap;transition:opacity .2s;}
  .btn-egpu-start:hover{opacity:.85;}
  .btn-egpu-stop{background:transparent;color:var(--muted);border:1px solid var(--border);
                 border-radius:5px;padding:6px 14px;font-family:var(--mono);font-size:0.72rem;
                 cursor:pointer;white-space:nowrap;transition:color .2s,border-color .2s;}
  .btn-egpu-stop:hover{color:var(--red);border-color:var(--red);}

  /* Dir manager */
  .dir-list{display:flex;flex-direction:column;gap:6px;margin-bottom:10px;}
  .dir-item{display:flex;align-items:center;gap:8px;padding:7px 10px;
            border-radius:5px;border:1px solid var(--border);background:var(--bg);}
  .dir-path{font-size:0.72rem;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--muted);}
  .dir-remove{background:transparent;border:none;color:var(--muted);cursor:pointer;
              font-size:0.9rem;padding:0 4px;height:auto;min-width:0;transition:color .15s;}
  .dir-remove:hover{color:var(--accent);}
  .dir-add-row{display:flex;gap:6px;}
  .dir-input{flex:1;background:var(--bg);border:1px solid var(--border);border-radius:4px;
             color:var(--text);font-family:var(--mono);font-size:0.75rem;
             padding:7px 10px;outline:none;transition:border-color .2s;}
  .dir-input:focus{border-color:var(--accent);}
  .dir-input::placeholder{color:var(--muted);}
  .btn-add{background:var(--accent);color:#000;border:none;border-radius:4px;
           padding:7px 14px;font-family:var(--sans);font-weight:700;font-size:0.75rem;
           cursor:pointer;white-space:nowrap;height:auto;letter-spacing:.03em;}
  .btn-add:hover{opacity:.85;}

  .model-list{display:flex;flex-direction:column;gap:6px;max-height:260px;overflow-y:auto;
              scrollbar-width:thin;scrollbar-color:var(--border) transparent;}
  .model-item{display:flex;align-items:center;gap:10px;padding:10px 12px;
              border-radius:6px;border:1px solid var(--border);cursor:pointer;
              transition:border-color .15s,background .15s;}
  .model-item:hover{background:var(--border);}
  .model-item.selected{border-color:var(--accent);background:rgba(255,107,53,.08);}
  .model-name{font-size:0.8rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .model-dir{font-size:0.6rem;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .model-size{font-size:0.65rem;color:var(--muted);flex-shrink:0;}

  .options{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px;}
  .opt-group{display:flex;flex-direction:column;gap:4px;}
  .opt-label{font-size:0.65rem;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;}
  .opt-input{background:var(--bg);border:1px solid var(--border);border-radius:4px;
             color:var(--text);font-family:var(--mono);font-size:0.8rem;
             padding:7px 10px;outline:none;transition:border-color .2s;}
  .opt-input:focus{border-color:var(--accent);}
  .opt-select{background:var(--bg);border:1px solid var(--border);border-radius:4px;
              color:var(--text);font-family:var(--mono);font-size:0.8rem;
              padding:7px 10px;outline:none;transition:border-color .2s;width:100%;cursor:pointer;}
  .opt-select:focus{border-color:var(--accent);}
  .opt-select option{background:var(--surface);}
  .btn-row{display:flex;gap:8px;margin-top:16px;}
  button{border:none;border-radius:7px;padding:10px 20px;font-family:var(--sans);
         font-weight:700;font-size:0.8rem;cursor:pointer;
         transition:opacity .2s,transform .1s;letter-spacing:.03em;}
  button:active{transform:scale(.97);}
  button:disabled{opacity:.3;cursor:not-allowed;}
  .btn-start{background:var(--green);color:#000;flex:1;}
  .btn-stop{background:var(--accent);color:#000;}
  .btn-chat{background:var(--accent2);color:#000;}
  .btn-llama-chat{background:#8b5cf6;color:#fff;}
  .btn-reload{background:transparent;color:var(--muted);border:1px solid var(--border);
              font-family:var(--mono);font-weight:400;font-size:0.75rem;}
  .status-bar{display:flex;align-items:center;gap:10px;padding:12px 16px;
              background:var(--bg);border:1px solid var(--border);border-radius:7px;
              margin-top:4px;}
  .dot{width:8px;height:8px;border-radius:50%;background:var(--muted);flex-shrink:0;transition:background .3s;}
  .dot.running{background:var(--green);box-shadow:0 0 8px var(--green);}
  .dot.error{background:var(--accent);box-shadow:0 0 8px var(--accent);}
  .status-txt{font-size:0.75rem;color:var(--muted);flex:1;}
  .status-txt.running{color:var(--green);}
  .status-txt.error{color:var(--accent);}
  .log{background:var(--bg);border:1px solid var(--border);border-radius:6px;
       padding:12px;font-size:0.7rem;line-height:1.7;color:var(--muted);
       max-height:160px;overflow-y:auto;white-space:pre-wrap;word-break:break-all;
       scrollbar-width:thin;scrollbar-color:var(--border) transparent;margin-top:8px;}
  .cmd-preview{font-size:0.68rem;color:var(--muted);background:var(--bg);
               border:1px solid var(--border);border-radius:6px;padding:10px 12px;
               margin-top:10px;white-space:pre-wrap;word-break:break-all;line-height:1.6;}
  .cmd-preview span{color:var(--accent2);}
  .no-models{text-align:center;padding:20px;color:var(--muted);font-size:0.8rem;}
   .warning{font-size:0.68rem;color:var(--accent);background:rgba(255,107,53,.08);
            border:1px solid rgba(255,107,53,.2);border-radius:5px;padding:8px 12px;margin-bottom:10px;}
   .dev-credit{font-family:var(--sans);font-size:1.2rem;font-weight:600;color:var(--accent);letter-spacing:-0.01em;margin-top:8px;text-align:center;}
</style>
</head>
<body>
<h1>Vega<span>56/64</span> Launcher</h1>
<div class="sub">llama.cpp · Vulkan · AMD RX Vega 56/64</div>
<div class="dev-credit">Entwickelt von bagueDev</div>

<!-- eGPU Panel -->
<div class="card">
  <div class="section-title">eGPU Status</div>
  <div class="egpu-panel">
    <div class="egpu-dot" id="egpuDot"></div>
    <div class="egpu-label" id="egpuLabel">Pruefe...</div>
    <button class="btn-egpu-stop" id="btnEgpuStop" onclick="stopEgpu()" style="display:none">■ Stop</button>
    <button class="btn-egpu-start" id="btnEgpuStart" onclick="startEgpu()">▶ egpu-alive starten</button>
  </div>
</div>

<!-- VERZEICHNISSE -->
<div class="card">
  <div class="section-title">Modell-Verzeichnisse</div>
  <div class="dir-list" id="dirList"></div>
  <div class="dir-add-row">
    <input class="dir-input" id="dirInput" placeholder="/Pfad/zu/gguf/Ordner" />
    <button class="btn-add" onclick="addDir()">+ Hinzufügen</button>
  </div>
</div>

<!-- MODELL PICKER -->
<div class="card">
  <div class="section-title">Modell wählen</div>
  <div id="egpuWarn" class="warning" style="display:none">
    ⚠ egpu-alive läuft nicht — eGPU könnte während Inference getrennt werden!
  </div>
  <div class="model-list" id="modelList">
    <div class="no-models">Lade Modelle...</div>
  </div>
  <div class="options">
    <div class="opt-group">
      <div class="opt-label">Kontext</div>
      <input class="opt-input" id="ctxSize" value="4096" type="number" step="512">
    </div>
    <div class="opt-group">
      <div class="opt-label">GPU Layers</div>
      <input class="opt-input" id="ngl" value="20" type="number">
    </div>
    <div class="opt-group">
      <div class="opt-label">Port</div>
      <input class="opt-input" id="port" value="8080" type="number">
    </div>
    <div class="opt-group">
      <div class="opt-label">Threads</div>
      <input class="opt-input" id="threads" value="6" type="number">
    </div>
    <div class="opt-group" style="grid-column:1/-1">
      <div class="opt-label">Chat Template</div>
      <select class="opt-select" id="chatTemplate">
        <option value="auto" selected>auto — aus GGUF-Metadaten (empfohlen)</option>
        <option value="chatml">chatml — Qwen3, Qwen2.5</option>
        <option value="llama3">llama3 — Llama 3 / 3.1 / 3.2</option>
        <option value="mistral">mistral — Mistral / Mixtral</option>
        <option value="mistral-v3">mistral-v3 — Mistral v3 Instruct</option>
        <option value="gemma">gemma — Gemma 2 / 3</option>
        <option value="gemma4">gemma4 — Gemma 4</option>
        <option value="phi3">phi3 — Phi-3 / 3.5</option>
        <option value="zephyr">zephyr — Zephyr</option>
      </select>
    </div>
  </div>
  <div class="cmd-preview" id="cmdPreview">← Modell wählen</div>
  <div class="btn-row">
    <button class="btn-start" id="btnStart" onclick="startServer()" disabled>▶ Starten</button>
    <button class="btn-stop"  id="btnStop"  onclick="stopServer()"  disabled>■ Stoppen</button>
    <button class="btn-chat"     id="btnChat"     onclick="openChat()"    disabled>Chat →</button>
    <button class="btn-llama-chat" id="btnLlamaChat" onclick="openLlamaChat()" disabled>🦙 Llama</button>
    <button class="btn-reload" onclick="loadModels()">⟳</button>
  </div>
</div>

<!-- STATUS -->
<div class="card">
  <div class="section-title">Status</div>
  <div class="status-bar">
    <div class="dot" id="dot"></div>
    <div class="status-txt" id="statusTxt">Server gestoppt</div>
  </div>
  <div class="log" id="log">Bereit.</div>
</div>

<script>
let selectedModel = null;
let pollInterval = null;
let egpuPollInterval = null;

// ── eGPU ────────────────────────────────────────────────────
async function pollEgpu() {
  try {
    const r = await fetch('/api/egpu/status');
    const d = await r.json();
    const dot   = document.getElementById('egpuDot');
    const label = document.getElementById('egpuLabel');
    const btnStart = document.getElementById('btnEgpuStart');
    const btnStop  = document.getElementById('btnEgpuStop');
    const warn  = document.getElementById('egpuWarn');
    if (d.running) {
      dot.className = 'egpu-dot running';
      label.className = 'egpu-label running';
      label.textContent = '● AMD Radeon RX Vega 56/64 — aktiv (PID ' + d.pid + ')';
      btnStart.style.display = 'none';
      btnStop.style.display  = 'inline-block';
      warn.style.display = 'none';
    } else {
      dot.className = 'egpu-dot';
      label.className = 'egpu-label';
      label.textContent = 'egpu-alive läuft nicht';
      btnStart.style.display = 'inline-block';
      btnStop.style.display  = 'none';
      warn.style.display = 'block';
    }
  } catch {}
}

async function startEgpu() {
  const btn = document.getElementById('btnEgpuStart');
  btn.disabled = true;
  btn.textContent = '...';
  const r = await fetch('/api/egpu/start', {method:'POST'});
  const d = await r.json();
  if (!d.ok) addLog('eGPU Fehler: ' + d.error);
  btn.disabled = false;
  btn.textContent = '▶ egpu-alive starten';
  pollEgpu();
}

async function stopEgpu() {
  await fetch('/api/egpu/stop', {method:'POST'});
  pollEgpu();
}

// Poll eGPU status every 3 seconds
pollEgpu();
egpuPollInterval = setInterval(pollEgpu, 3000);

// ── Verzeichnis-Manager ──────────────────────────────────────
function renderDirs(dirs) {
  const list = document.getElementById('dirList');
  list.innerHTML = '';
  dirs.forEach(d => {
    const el = document.createElement('div');
    el.className = 'dir-item';
    el.innerHTML =
      '<div class="dir-path">' + d + '</div>' +
      '<button class="dir-remove" onclick="removeDir(\'' + d.replace(/\\/g,'\\\\').replace(/'/g,"\\'") + '\')" title="Entfernen">&#10005;</button>';
    list.appendChild(el);
  });
}

async function loadDirs() {
  const r = await fetch('/api/dirs');
  const dirs = await r.json();
  renderDirs(dirs);
}

async function addDir() {
  const input = document.getElementById('dirInput');
  const path = input.value.trim();
  if (!path) return;
  const r = await fetch('/api/dirs/add', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({path})
  });
  const d = await r.json();
  if (d.ok) { input.value = ''; renderDirs(d.dirs); loadModels(); }
  else addLog('Fehler: ' + d.error);
}

async function removeDir(path) {
  const r = await fetch('/api/dirs/remove', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({path})
  });
  const d = await r.json();
  renderDirs(d.dirs);
  loadModels();
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('dirInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') addDir();
  });
});

// ── Modelle ──────────────────────────────────────────────────
async function loadModels() {
  const list = document.getElementById('modelList');
  list.innerHTML = '<div class="no-models">Lade...</div>';
  try {
    const r = await fetch('/api/models');
    const models = await r.json();
    if (!models.length) {
      list.innerHTML = '<div class="no-models">Keine .gguf Dateien gefunden</div>';
      return;
    }
    list.innerHTML = '';
    models.forEach(m => {
      const el = document.createElement('div');
      el.className = 'model-item';
      el.innerHTML =
        '<div style="flex:1;min-width:0">' +
          '<div class="model-name">' + m.name + '</div>' +
          '<div class="model-dir">' + m.dir + '</div>' +
        '</div>' +
        '<div class="model-size">' + m.size + '</div>';
      el.onclick = () => selectModel(m, el);
      list.appendChild(el);
    });
  } catch(e) {
    list.innerHTML = '<div class="no-models">Fehler beim Laden</div>';
  }
}

function selectModel(m, el) {
  document.querySelectorAll('.model-item').forEach(i => i.classList.remove('selected'));
  el.classList.add('selected');
  selectedModel = m;
  document.getElementById('btnStart').disabled = false;
  updatePreview();
}

function updatePreview() {
  if (!selectedModel) return;
  const ctx = document.getElementById('ctxSize').value;
  const ngl = document.getElementById('ngl').value;
  const port = document.getElementById('port').value;
  const threads = document.getElementById('threads').value;
  const tpl = document.getElementById('chatTemplate').value;
  document.getElementById('cmdPreview').innerHTML =
    '<span>llama-server</span> -m ' + selectedModel.name +
    ' -ngl ' + ngl + ' --device Vulkan0' +
    ' --ctx-size ' + ctx + ' --threads ' + threads + ' --port ' + port +
    ' --chat-template ' + tpl;
}

['ctxSize','ngl','port','threads','chatTemplate'].forEach(id =>
  document.getElementById(id).addEventListener('input', updatePreview)
);

// ── Server ───────────────────────────────────────────────────
async function startServer() {
  if (!selectedModel) return;
  document.getElementById('btnStart').disabled = true;
  setStatus('starting', 'Starte Server...');
  addLog('Starte: ' + selectedModel.name);
  const body = {
    model: selectedModel.path,
    ctx_size: parseInt(document.getElementById('ctxSize').value),
    ngl: parseInt(document.getElementById('ngl').value),
    port: parseInt(document.getElementById('port').value),
    threads: parseInt(document.getElementById('threads').value),
    chat_template: document.getElementById('chatTemplate').value,
  };
  try {
    const r = await fetch('/api/start', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify(body)
    });
    const d = await r.json();
    if (d.ok) {
      document.getElementById('btnStop').disabled = false;
      document.getElementById('btnChat').disabled = false;
      document.getElementById('btnLlamaChat').disabled = false;
      pollStatus();
    } else {
      setStatus('error', 'Fehler: ' + d.error);
      document.getElementById('btnStart').disabled = false;
    }
  } catch(e) {
    setStatus('error', 'Fehler: ' + e.message);
    document.getElementById('btnStart').disabled = false;
  }
}

async function stopServer() {
  await fetch('/api/stop', {method:'POST'});
  clearInterval(pollInterval);
  setStatus('stopped', 'Server gestoppt');
  addLog('Server gestoppt.');
  document.getElementById('btnStart').disabled = !selectedModel;
  document.getElementById('btnStop').disabled = true;
  document.getElementById('btnChat').disabled = true;
  document.getElementById('btnLlamaChat').disabled = true;
}

function pollStatus() {
  clearInterval(pollInterval);
  pollInterval = setInterval(async () => {
    try {
      const r = await fetch('/api/status');
      const d = await r.json();
      if (d.running) {
        setStatus('running', 'Läuft · Port ' + d.port + ' · ' + d.model);
        if (d.log_line) addLog(d.log_line);
      } else {
        setStatus('stopped', 'Server gestoppt');
        clearInterval(pollInterval);
        document.getElementById('btnStart').disabled = !selectedModel;
        document.getElementById('btnStop').disabled = true;
        document.getElementById('btnChat').disabled = true;
        document.getElementById('btnLlamaChat').disabled = true;
      }
    } catch {}
  }, 1500);
}

function setStatus(state, text) {
  const dot = document.getElementById('dot');
  const txt = document.getElementById('statusTxt');
  dot.className = 'dot' + (state === 'running' ? ' running' : state === 'error' ? ' error' : '');
  txt.className = 'status-txt' + (state === 'running' ? ' running' : state === 'error' ? ' error' : '');
  txt.textContent = text;
}

function addLog(line) {
  const log = document.getElementById('log');
  log.textContent += '\n' + line;
  log.scrollTop = log.scrollHeight;
}

function openChat() {
  const port = document.getElementById('port').value;
  const ctx = document.getElementById('ctxSize').value;
  window.location.href = '/chat?port=' + port + '&ctx=' + ctx;
}

function openLlamaChat() {
  const port = document.getElementById('port').value;
  window.open('http://localhost:' + port, '_blank');
}

loadDirs();
loadModels();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# HTML CHAT
# ─────────────────────────────────────────────────────────────────────────────

HTML_CHAT = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vega56/64 Chat</title>
<style>
  :root {
    --bg: #0a0a0f;--surface: #111118;--border: #1e1e2e;--accent: #ff6b35;
    --accent2: #e040fb;--text: #e8e8f0;--muted: #555570;--green: #00e5a0;--red: #ff4757;
    --mono: ui-monospace,'SF Mono','Menlo','Courier New',monospace;
    --sans: -apple-system,BlinkMacSystemFont,'Helvetica Neue',sans-serif;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: var(--bg);color: var(--text);font-family: var(--mono);
    height: 100vh;display: grid;
    grid-template-rows: auto 1fr auto;grid-template-columns: 1fr 280px;
    grid-template-areas: "header header" "chat sidebar" "input sidebar";
    overflow: hidden;
  }
  header {
    grid-area: header;padding: 14px 24px;border-bottom: 1px solid var(--border);
    display: flex;align-items: center;gap: 12px;background: var(--surface);
  }
  .back-btn {
    background: transparent;color: var(--muted);border: 1px solid var(--border);
    border-radius: 6px;padding: 6px 12px;font-family: var(--mono);font-size: 0.72rem;
    cursor: pointer;height: 30px;transition: color .2s,border-color .2s;
  }
  .back-btn:hover { color: var(--text); border-color: var(--muted); }
  .logo { font-family: var(--sans);font-weight: 800;font-size: 1.1rem;color: var(--accent);letter-spacing: -0.02em; }
  .logo span { color: var(--text); }
  .status-dot { width: 8px;height: 8px;border-radius: 50%;background: var(--muted);transition: background .3s;flex-shrink: 0; }
  .status-dot.online { background: var(--green);box-shadow: 0 0 8px var(--green); }
  .status-dot.error { background: var(--accent); }
  .status-text { font-size: 0.7rem;color: var(--muted);letter-spacing: .05em;text-transform: uppercase; }
  .model-badge { margin-left: auto;font-size: 0.65rem;color: var(--muted);background: var(--border);
                 padding: 4px 10px;border-radius: 4px;max-width: 300px;overflow: hidden;
                 text-overflow: ellipsis;white-space: nowrap; }

  /* eGPU mini-panel in header */
  .egpu-mini { display:flex;align-items:center;gap:7px;padding:4px 10px;
               border:1px solid var(--border);border-radius:5px;cursor:pointer;
               transition:border-color .2s;flex-shrink:0; }
  .egpu-mini:hover { border-color: var(--muted); }
  .egpu-mini-dot { width:7px;height:7px;border-radius:50%;background:var(--muted);transition:background .3s; }
  .egpu-mini-dot.running { background:var(--green);box-shadow:0 0 6px var(--green); }
  .egpu-mini-dot.error { background:var(--red); }
  .egpu-mini-label { font-size:0.65rem;color:var(--muted);white-space:nowrap; }
  .egpu-mini-label.running { color:var(--green); }

  #chat { grid-area: chat;overflow-y: auto;padding: 20px 24px;display: flex;
          flex-direction: column;gap: 16px;
          scrollbar-width: thin;scrollbar-color: var(--border) transparent; }

  /* Scroll-to-bottom hint */
  .scroll-hint { position:fixed;bottom:110px;left:50%;transform:translateX(-50%);
                 background:var(--surface);border:1px solid var(--border);border-radius:20px;
                 padding:6px 16px;font-size:0.72rem;color:var(--muted);cursor:pointer;
                 transition:opacity .2s;z-index:10;display:none; }
  .scroll-hint:hover { color:var(--text); }

  .msg { display: flex;gap: 12px;animation: fadeUp 0.2s ease;position:relative; }
  @keyframes fadeUp { from { opacity: 0;transform: translateY(6px); } to { opacity: 1;transform: translateY(0); } }
  .msg-role { font-size: 0.6rem;text-transform: uppercase;letter-spacing: .1em;padding-top: 3px;flex-shrink: 0;width: 40px; }
  .msg.user .msg-role { color: var(--accent); }
  .msg.assistant .msg-role { color: var(--accent2); }
  .msg.system .msg-role { color: var(--muted); }
  .msg-content { font-size: 0.85rem;line-height: 1.7;color: var(--text);flex: 1;white-space: pre-wrap;word-break: break-word; }
  .msg.user .msg-content { color: #c8c8e0; }

  /* Copy button per message */
  .msg-copy { position:absolute;top:0;right:0;background:transparent;
              border:1px solid transparent;border-radius:4px;padding:3px 8px;
              font-size:0.65rem;color:var(--muted);cursor:pointer;
              opacity:0;transition:opacity .15s,color .15s,border-color .15s; }
  .msg:hover .msg-copy { opacity:1; }
  .msg-copy:hover { color:var(--text);border-color:var(--border); }
  .msg-copy.copied { color:var(--green);border-color:var(--green); }

  .cursor { display: inline-block;width: 2px;height: 1em;background: var(--accent2);
            animation: blink .8s infinite;vertical-align: text-bottom;margin-left: 2px; }
  @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }

  .input-area { grid-area: input;padding: 16px 24px 20px;border-top: 1px solid var(--border);
                background: var(--surface);display: flex;gap: 10px;align-items: flex-end; }
  textarea { flex: 1;background: var(--bg);border: 1px solid var(--border);border-radius: 8px;
             color: var(--text);font-family: var(--mono);font-size: 0.85rem;padding: 10px 14px;
             resize: none;min-height: 44px;max-height: 140px;outline: none;
             transition: border-color .2s;line-height: 1.5; }
  textarea:focus { border-color: var(--accent); }
  textarea::placeholder { color: var(--muted); }
  button { background: var(--accent);color: #000;border: none;border-radius: 8px;padding: 10px 18px;
           font-family: var(--sans);font-weight: 700;font-size: 0.8rem;cursor: pointer;
           transition: opacity .2s,transform .1s;white-space: nowrap;height: 44px;letter-spacing: .03em; }
  button:hover { opacity: .85; }
  button:active { transform: scale(.97); }
  button:disabled { opacity: .3;cursor: not-allowed; }
  .btn-clear { background: transparent;color: var(--muted);border: 1px solid var(--border);
               font-family: var(--mono);font-weight: 400;font-size: .75rem; }
  .btn-export { background: transparent;color: var(--muted);border: 1px solid var(--border);
                font-family: var(--mono);font-weight: 400;font-size: .75rem; }
  .btn-export:hover { color:var(--green);border-color:var(--green);opacity:1; }

  aside { grid-area: sidebar;border-left: 1px solid var(--border);background: var(--surface);
          padding: 20px 16px;overflow-y: auto;display: flex;flex-direction: column;gap: 20px;
          scrollbar-width: thin;scrollbar-color: var(--border) transparent; }
  .section-title { font-family: var(--sans);font-size: .65rem;text-transform: uppercase;
                   letter-spacing: .12em;color: var(--muted);margin-bottom: 10px; }
  .stat-grid { display: grid;grid-template-columns: 1fr 1fr;gap: 8px; }
  .stat-card { background: var(--bg);border: 1px solid var(--border);border-radius: 6px;padding: 10px 12px; }
  .stat-label { font-size: .6rem;color: var(--muted);text-transform: uppercase;letter-spacing: .08em;margin-bottom: 4px; }
  .stat-value { font-size: 1.1rem;font-weight: 600;color: var(--text); }
  .stat-value.green { color: var(--green); }
  .stat-value.orange { color: var(--accent); }
  .stat-value.purple { color: var(--accent2); }
  .stat-value.blue { color: #60a5fa; }
  .token-bar-wrap { background: var(--bg);border: 1px solid var(--border);border-radius: 6px;padding: 10px 12px; }
  .token-bar-label { display: flex;justify-content: space-between;font-size: .65rem;color: var(--muted);margin-bottom: 6px; }
  .token-bar { height: 4px;background: var(--border);border-radius: 2px;overflow: hidden; }
  .token-bar-fill { height: 100%;background: linear-gradient(90deg,var(--green),var(--accent2));
                    border-radius: 2px;transition: width .3s;width: 0%; }
  .api-block { background: var(--bg);border: 1px solid var(--border);border-radius: 6px;padding: 10px 12px; }
  .api-url { font-size: .7rem;color: var(--green);word-break: break-all;margin-bottom: 8px; }
  .api-snippet { font-size: .62rem;color: var(--muted);line-height: 1.6;white-space: pre;overflow-x: auto; }
  .empty-state { text-align: center;padding: 40px 20px;color: var(--muted);font-size: .8rem;line-height: 1.8; }
  .empty-state .big { font-size: 2rem;margin-bottom: 8px; }
  .sysprompt { width: 100%;height: 80px;background: var(--bg);border: 1px solid var(--border);
               border-radius: 6px;color: var(--text);font-family: var(--mono);font-size: .72rem;
               padding: 8px 10px;resize: vertical;outline: none;transition: border-color .2s; }
  .sysprompt:focus { border-color: var(--accent); }

  /* eGPU sidebar card */
  .egpu-card { background:var(--bg);border:1px solid var(--border);border-radius:6px;padding:12px; }
  .egpu-row { display:flex;align-items:center;gap:8px;margin-bottom:8px; }
  .egpu-s-dot { width:8px;height:8px;border-radius:50%;background:var(--muted);flex-shrink:0;transition:background .3s; }
  .egpu-s-dot.running { background:var(--green);box-shadow:0 0 6px var(--green); }
  .egpu-s-label { font-size:0.72rem;flex:1;color:var(--muted); }
  .egpu-s-label.running { color:var(--green); }
  .btn-egpu-sm { border:none;border-radius:5px;padding:5px 12px;font-family:var(--sans);
                 font-weight:700;font-size:0.68rem;cursor:pointer;width:100%;
                 transition:opacity .2s;height:auto; }
  .btn-egpu-sm.start { background:var(--green);color:#000; }
  .btn-egpu-sm.stop  { background:transparent;color:var(--muted);border:1px solid var(--border); }
  .btn-egpu-sm:hover { opacity:.85; }
</style>
</head>
<body>
<header>
  <button class="back-btn" onclick="window.location.href='/'">&#8592; Launcher</button>
  <div class="logo">Vega<span>56/64</span> Chat</div>
  <div class="status-dot" id="statusDot"></div>
  <div class="status-text" id="statusText">verbinde...</div>

  <!-- eGPU mini-status in header -->
  <div class="egpu-mini" onclick="document.getElementById('sidebarEgpu').scrollIntoView({behavior:'smooth'})" title="eGPU Status">
    <div class="egpu-mini-dot" id="egpuMiniDot"></div>
    <div class="egpu-mini-label" id="egpuMiniLabel">eGPU</div>
  </div>

  <div class="model-badge" id="modelBadge">&#8212;</div>
</header>

<!-- Scroll-to-bottom hint -->
<div class="scroll-hint" id="scrollHint" onclick="scrollToBottom(true)">↓ neue Nachricht</div>

<div id="chat">
  <div class="empty-state"><div class="big">&#9889;</div>Verbinde mit llama-server...</div>
</div>

<div class="input-area">
  <textarea id="input" placeholder="Nachricht... (Enter = senden, Shift+Enter = Zeilenumbruch)" rows="1"></textarea>
  <button class="btn-clear" onclick="clearChat()">Leeren</button>
  <button class="btn-export" onclick="exportChat()" title="Als Markdown exportieren">↓ MD</button>
  <button id="sendBtn" onclick="sendMessage()" disabled>Senden</button>
</div>

<aside>
  <!-- eGPU sidebar panel -->
  <div id="sidebarEgpu">
    <div class="section-title">eGPU</div>
    <div class="egpu-card">
      <div class="egpu-row">
        <div class="egpu-s-dot" id="egpuSDot"></div>
        <div class="egpu-s-label" id="egpuSLabel">Pruefe...</div>
      </div>
      <button class="btn-egpu-sm start" id="btnEgpuSmStart" onclick="startEgpu()">▶ egpu-alive starten</button>
      <button class="btn-egpu-sm stop"  id="btnEgpuSmStop"  onclick="stopEgpu()" style="display:none;margin-top:5px">■ Stoppen</button>
    </div>
  </div>

  <div>
    <div class="section-title">Token Monitor</div>
    <div class="stat-grid">
      <div class="stat-card"><div class="stat-label">Tokens/s</div><div class="stat-value green" id="statTps">&#8212;</div></div>
      <div class="stat-card"><div class="stat-label">Gesamt</div><div class="stat-value orange" id="statTotal">0</div></div>
      <div class="stat-card"><div class="stat-label">Prompt</div><div class="stat-value" id="statPrompt">0</div></div>
      <div class="stat-card"><div class="stat-label">Antwort</div><div class="stat-value purple" id="statCompletion">0</div></div>
      <div class="stat-card"><div class="stat-label">Letzte Antwort</div><div class="stat-value blue" id="statTime">&#8212;</div></div>
      <div class="stat-card"><div class="stat-label">Gesamt Zeit</div><div class="stat-value" id="statTimeTotal">0s</div></div>
    </div>
    <div style="margin-top:8px">
      <div class="token-bar-wrap">
        <div class="token-bar-label"><span>Kontext</span><span id="ctxUsed">0 / 4096</span></div>
        <div class="token-bar"><div class="token-bar-fill" id="ctxBar"></div></div>
      </div>
    </div>
  </div>

  <div>
    <div class="section-title">System Prompt</div>
    <textarea class="sysprompt" id="sysprompt" placeholder="Optional: Rolle / Anweisung..."></textarea>
  </div>

  <div>
    <div class="section-title">Continue.dev</div>
    <div class="api-block">
      <div class="api-url" id="apiUrl">&#8212;</div>
      <div class="api-snippet" id="apiSnippet">Verbinde zuerst...</div>
    </div>
  </div>
</aside>

<script>
  const params = new URLSearchParams(window.location.search);
  const SERVER_PORT = params.get('port') || 8080;
  const SERVER_CTX = parseInt(params.get('ctx')) || 4096;
  const SERVER_URL  = 'http://localhost:' + SERVER_PORT;
  let messages = [], totalPromptTokens = 0, totalCompletionTokens = 0;
  let ctxLimit = 4096, isConnected = false;

  // Token-Schätzung: ~4 Zeichen pro Token
  function estimateTokens(text) { return Math.ceil((text || '').length / 4); }
  function estimatePromptTokens(msgs) {
    return msgs.reduce((sum, m) => sum + estimateTokens(m.content) + 4, 0) + 2;
  }

  let totalElapsed = 0;
  let timerInterval = null;
  let egpuPollInterval = null;

  const chatEl  = document.getElementById('chat');
  const inputEl = document.getElementById('input');
  const sendBtn = document.getElementById('sendBtn');

  // ── Smart Scroll ────────────────────────────────────────────
  // Track if user has scrolled up manually
  let userScrolledUp = false;
  let isStreaming = false;

  chatEl.addEventListener('scroll', () => {
    const threshold = 60;
    const atBottom = chatEl.scrollHeight - chatEl.scrollTop - chatEl.clientHeight < threshold;
    if (atBottom) {
      userScrolledUp = false;
      document.getElementById('scrollHint').style.display = 'none';
    } else if (isStreaming) {
      userScrolledUp = true;
      document.getElementById('scrollHint').style.display = 'block';
    }
  });

  function scrollToBottom(force) {
    if (force || !userScrolledUp) {
      chatEl.scrollTop = chatEl.scrollHeight;
      userScrolledUp = false;
      document.getElementById('scrollHint').style.display = 'none';
    }
  }

  // ── eGPU ────────────────────────────────────────────────────
  async function pollEgpu() {
    try {
      const r = await fetch('/api/egpu/status');
      const d = await r.json();

      // Header mini-dot
      const miniDot   = document.getElementById('egpuMiniDot');
      const miniLabel = document.getElementById('egpuMiniLabel');
      // Sidebar
      const sDot   = document.getElementById('egpuSDot');
      const sLabel = document.getElementById('egpuSLabel');
      const btnStart = document.getElementById('btnEgpuSmStart');
      const btnStop  = document.getElementById('btnEgpuSmStop');

      if (d.running) {
        miniDot.className = 'egpu-mini-dot running';
        miniLabel.className = 'egpu-mini-label running';
        miniLabel.textContent = 'eGPU ●';
        sDot.className = 'egpu-s-dot running';
        sLabel.className = 'egpu-s-label running';
        sLabel.textContent = 'AMD Vega 56/64 aktiv (PID ' + d.pid + ')';
        btnStart.style.display = 'none';
        btnStop.style.display  = 'block';
      } else {
        miniDot.className = 'egpu-mini-dot error';
        miniLabel.className = 'egpu-mini-label';
        miniLabel.textContent = 'eGPU ○';
        sDot.className = 'egpu-s-dot';
        sLabel.className = 'egpu-s-label';
        sLabel.textContent = 'egpu-alive läuft nicht';
        btnStart.style.display = 'block';
        btnStop.style.display  = 'none';
      }
    } catch {}
  }

  async function startEgpu() {
    const btn = document.getElementById('btnEgpuSmStart');
    btn.disabled = true; btn.textContent = '...';
    const r = await fetch('/api/egpu/start', {method:'POST'});
    btn.disabled = false; btn.textContent = '▶ egpu-alive starten';
    pollEgpu();
  }

  async function stopEgpu() {
    await fetch('/api/egpu/stop', {method:'POST'});
    pollEgpu();
  }

  pollEgpu();
  egpuPollInterval = setInterval(pollEgpu, 3000);

  // ── Connect ──────────────────────────────────────────────────
  inputEl.addEventListener('input', () => {
    inputEl.style.height = 'auto';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 140) + 'px';
  });
  inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (!sendBtn.disabled) sendMessage(); }
  });

  async function connect() {
    try {
      const r = await fetch(SERVER_URL + '/v1/models', {signal: AbortSignal.timeout(4000)});
      if (!r.ok) throw new Error();
      const data = await r.json();
      console.log('Models API response:', data);
      const modelName = data.data?.[0]?.id || 'local';
      // Try different field names for context length, fallback to URL param or 4096
      ctxLimit = data.data?.[0]?.context_length 
              || data.data?.[0]?.llama?.context_length 
              || data.data?.[0]?.properties?.context_length 
              || SERVER_CTX;
      document.getElementById('statusDot').className = 'status-dot online';
      document.getElementById('statusText').textContent = 'verbunden';
      document.getElementById('modelBadge').textContent = modelName;
      document.getElementById('apiUrl').textContent = SERVER_URL + '/v1';
      document.getElementById('ctxUsed').textContent = '0 / ' + ctxLimit;
      document.getElementById('apiSnippet').textContent =
        '- name: Vega56/64\n  provider: openai\n  model: ' + modelName + '\n  apiBase: ' + SERVER_URL + '/v1\n  apiKey: none';
      isConnected = true;
      sendBtn.disabled = false;
      addSystemMsg('Verbunden: ' + modelName + ' auf Port ' + SERVER_PORT + ' (ctx: ' + ctxLimit + ')');
    } catch {
      document.getElementById('statusDot').className = 'status-dot error';
      document.getElementById('statusText').textContent = 'fehler';
      addSystemMsg('Kein Server auf Port ' + SERVER_PORT);
      setTimeout(connect, 4000);
    }
  }

  function addSystemMsg(text) {
    if (chatEl.querySelector('.empty-state')) chatEl.innerHTML = '';
    const el = document.createElement('div'); el.className = 'msg system';
    el.innerHTML = '<div class="msg-role">sys</div><div class="msg-content">' + text + '</div>';
    chatEl.appendChild(el);
    scrollToBottom(true);
  }

  function escHtml(t) { return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  // ── Copy per message ─────────────────────────────────────────
  function makeCopyBtn(getContent) {
    const btn = document.createElement('button');
    btn.className = 'msg-copy';
    btn.textContent = 'kopieren';
    btn.onclick = () => {
      navigator.clipboard.writeText(getContent()).then(() => {
        btn.textContent = '✓ kopiert';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = 'kopieren'; btn.classList.remove('copied'); }, 2000);
      });
    };
    return btn;
  }

  // ── Export as Markdown ───────────────────────────────────────
  function exportChat() {
    if (!messages.length) return;
    const modelName = document.getElementById('modelBadge').textContent || 'local';
    const sp = document.getElementById('sysprompt').value.trim();
    const now = new Date().toISOString().replace('T', ' ').slice(0, 19);
    let md = '# Vega56/64 Chat Export\n\n';
    md += `**Modell:** ${modelName}  \n`;
    md += `**Datum:** ${now}  \n`;
    md += `**Port:** ${SERVER_PORT}\n\n`;
    if (sp) md += `**System Prompt:** ${sp}\n\n`;
    md += '---\n\n';
    messages.forEach(m => {
      const role = m.role === 'user' ? '**Du**' : '**KI**';
      md += `${role}\n\n${m.content}\n\n---\n\n`;
    });
    const blob = new Blob([md], {type: 'text/markdown'});
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url;
    a.download = 'vega56-64-chat-' + now.replace(/[ :]/g, '-') + '.md';
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── Send ─────────────────────────────────────────────────────
  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text || !isConnected) return;
    inputEl.value = ''; inputEl.style.height = 'auto'; sendBtn.disabled = true;
    messages.push({role: 'user', content: text});

    // User bubble
    const uel = document.createElement('div'); uel.className = 'msg user';
    const ucopyBtn = makeCopyBtn(() => text);
    uel.innerHTML = '<div class="msg-role">du</div><div class="msg-content">' + escHtml(text) + '</div>';
    uel.appendChild(ucopyBtn);
    chatEl.appendChild(uel);
    scrollToBottom(true);

    // Assistant bubble
    const ael = document.createElement('div'); ael.className = 'msg assistant';
    const cur = document.createElement('span'); cur.className = 'cursor';
    const ac  = document.createElement('div');  ac.className  = 'msg-content'; ac.appendChild(cur);
    ael.innerHTML = '<div class="msg-role">ki</div>'; ael.appendChild(ac);
    chatEl.appendChild(ael);
    scrollToBottom(true);

    let response = '', ct = 0, t0 = Date.now();
    const sp = document.getElementById('sysprompt').value.trim();
    const apiMsgs = [...(sp ? [{role:'system', content:sp}] : []), ...messages];

    // Prompt-Tokens schätzen und anzeigen
    totalPromptTokens = estimatePromptTokens(apiMsgs);
    document.getElementById('statPrompt').textContent = totalPromptTokens;

    // Live timer
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      document.getElementById('statTime').textContent = ((Date.now()-t0)/1000).toFixed(1) + 's';
    }, 100);

    isStreaming = true;
    userScrolledUp = false;

    try {
      const r = await fetch(SERVER_URL + '/v1/chat/completions', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({model: 'local', messages: apiMsgs, stream: true, max_tokens: 2048})
      });
      const reader = r.body.getReader(), decoder = new TextDecoder();
      while (true) {
        const {done, value} = await reader.read(); if (done) break;
        for (const line of decoder.decode(value).split('\n')) {
          if (!line.startsWith('data: ')) continue;
          const d = line.slice(6).trim(); if (d === '[DONE]') continue;
          try {
            const j = JSON.parse(d);
            const delta = j.choices?.[0]?.delta?.content || '';
            response += delta; ct++;
            ac.textContent = response; ac.appendChild(cur);
            // Smart scroll: only auto-scroll if user hasn't scrolled up
            scrollToBottom(false);
            const el = (Date.now() - t0) / 1000;
            document.getElementById('statTps').textContent = el > 0 ? (ct/el).toFixed(1) : '--';
            document.getElementById('statCompletion').textContent = ct;
            // Update ctx usage with estimated prompt tokens + completion tokens
            const used = totalPromptTokens + ct;
            document.getElementById('ctxUsed').textContent = used + ' / ' + ctxLimit;
            document.getElementById('ctxBar').style.width = Math.min(used/ctxLimit*100, 100) + '%';
          } catch {}
        }
      }

      clearInterval(timerInterval);
      isStreaming = false;
      const elapsed = (Date.now() - t0) / 1000;
      totalElapsed += elapsed;
      document.getElementById('statTime').textContent = elapsed.toFixed(1) + 's';
      document.getElementById('statTimeTotal').textContent = totalElapsed.toFixed(1) + 's';

      cur.remove();
      messages.push({role: 'assistant', content: response});

      // Add copy button to assistant message after streaming done
      const acopyBtn = makeCopyBtn(() => response);
      ael.appendChild(acopyBtn);

      totalCompletionTokens += ct;
      document.getElementById('statTps').textContent = elapsed > 0 ? (ct/elapsed).toFixed(1) : '--';
      document.getElementById('statTotal').textContent = totalPromptTokens + totalCompletionTokens;
      document.getElementById('statPrompt').textContent = totalPromptTokens;
      document.getElementById('statCompletion').textContent = totalCompletionTokens;

    } catch(e) {
      clearInterval(timerInterval);
      isStreaming = false;
      cur.remove(); ac.textContent = 'Fehler: ' + e.message;
    }
    sendBtn.disabled = false; inputEl.focus();
  }

  function clearChat() {
    messages = []; totalPromptTokens = 0; totalCompletionTokens = 0; totalElapsed = 0;
    clearInterval(timerInterval);
    userScrolledUp = false;
    isStreaming = false;
    document.getElementById('scrollHint').style.display = 'none';
    chatEl.innerHTML = '<div class="empty-state"><div class="big">&#9889;</div>Chat geleert.</div>';
    ['statTps','statTime'].forEach(id => document.getElementById(id).textContent = '--');
    ['statTotal','statPrompt','statCompletion'].forEach(id => document.getElementById(id).textContent = '0');
    document.getElementById('statTimeTotal').textContent = '0s';
    document.getElementById('ctxUsed').textContent = '0 / ' + ctxLimit;
    document.getElementById('ctxBar').style.width = '0%';
  }

  connect();
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# HTTP HANDLER
# ─────────────────────────────────────────────────────────────────────────────


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/":
            body = HTML_LAUNCHER.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        elif path == "/chat":
            body = HTML_CHAT.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        elif path == "/api/models":
            global models_dirs
            models = []
            seen = set()
            for d in models_dirs:
                p = Path(d)
                if p.exists():
                    for f in sorted(p.glob("*.gguf")):
                        if f.name not in seen:
                            seen.add(f.name)
                            size_mb = f.stat().st_size / (1024 * 1024)
                            size_str = (
                                f"{size_mb / 1024:.1f} GB"
                                if size_mb >= 1024
                                else f"{size_mb:.0f} MB"
                            )
                            models.append(
                                {
                                    "name": f.name,
                                    "path": str(f),
                                    "size": size_str,
                                    "dir": d,
                                }
                            )
            self.send_json(models)

        elif path == "/api/dirs":
            self.send_json(models_dirs)

        elif path == "/api/status":
            global server_process
            running = server_process is not None and server_process.poll() is None
            log_line = ""
            if running and server_process.stderr:
                try:
                    import select

                    if select.select([server_process.stderr], [], [], 0)[0]:
                        log_line = (
                            server_process.stderr.readline()
                            .decode(errors="replace")
                            .strip()
                        )
                except Exception:
                    pass
            self.send_json(
                {
                    "running": running,
                    "port": SERVER_PORT,
                    "model": Path(models_dirs[0]).name
                    if running and models_dirs
                    else "",
                    "log_line": log_line,
                }
            )

        elif path == "/api/egpu/status":
            global egpu_process
            running = egpu_process is not None and egpu_process.poll() is None
            pid = egpu_process.pid if running else None
            # Also check if any other egpu-alive is running
            if not running:
                try:
                    result = subprocess.run(
                        ["pgrep", "-f", "egpu-alive"], capture_output=True, text=True
                    )
                    pids = result.stdout.strip().split()
                    if pids:
                        running = True
                        pid = int(pids[0])
                except Exception:
                    pass
            self.send_json({"running": running, "pid": pid})

        elif path == "/api/config":
            self.send_json({"models_dirs": models_dirs})

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global server_process, egpu_process, SERVER_PORT, models_dirs

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}

        if self.path == "/api/start":
            if server_process and server_process.poll() is None:
                server_process.terminate()
                server_process.wait()
            SERVER_PORT = body.get("port", 8080)
            tpl = body.get("chat_template", "auto")
            cmd = [
                LLAMA_SERVER,
                "-m",
                body["model"],
                "-ngl",
                str(body.get("ngl", 99)),
                "--device",
                "Vulkan0",
                "--ctx-size",
                str(body.get("ctx_size", 4096)),
                "--threads",
                str(body.get("threads", 6)),
                "--port",
                str(SERVER_PORT),
                "--host",
                "0.0.0.0",
                "--cache-type-k",
                "f16",
                "--cache-type-v",
                "f16",
                "--jinja",
                "--no-warmup",
                "--webui-mcp-proxy",
            ]
            # Only add --chat-template if not auto (auto = let llama.cpp read from GGUF)
            if tpl and tpl != "auto":
                cmd += ["--chat-template", tpl]
            try:
                server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    cwd=LLAMA_CPP_DIR,
                )
                self.send_json({"ok": True})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 500)

        elif self.path == "/api/stop":
            if server_process and server_process.poll() is None:
                server_process.terminate()
                server_process.wait()
            self.send_json({"ok": True})

        elif self.path == "/api/egpu/start":
            # Kill any stale process first
            if egpu_process and egpu_process.poll() is None:
                egpu_process.terminate()
            try:
                egpu_process = subprocess.Popen(
                    [EGPU_ALIVE_BIN],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self.send_json({"ok": True, "pid": egpu_process.pid})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})

        elif self.path == "/api/egpu/stop":
            stopped = False
            if egpu_process and egpu_process.poll() is None:
                egpu_process.terminate()
                stopped = True
            # Also kill any external egpu-alive processes
            try:
                subprocess.run(["pkill", "-f", "egpu-alive"], capture_output=True)
                stopped = True
            except Exception:
                pass
            self.send_json({"ok": stopped})

        elif self.path == "/api/dirs/add":
            path = body.get("path", "").strip()
            if not path:
                self.send_json({"ok": False, "error": "Kein Pfad angegeben"})
                return
            p = Path(path)
            if not p.exists():
                self.send_json(
                    {"ok": False, "error": "Verzeichnis nicht gefunden: " + path}
                )
                return
            if path not in models_dirs:
                models_dirs.append(path)
            self.send_json({"ok": True, "dirs": models_dirs})

        elif self.path == "/api/dirs/remove":
            path = body.get("path", "")
            if path in models_dirs and len(models_dirs) > 1:
                models_dirs.remove(path)
            self.send_json({"ok": True, "dirs": models_dirs})

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────


def main():
    print(f"Vega56/64 Launcher  ->  http://localhost:{LAUNCHER_PORT}")
    print(f"Modelle: {DEFAULT_MODELS}")
    print(f"llama-server: {LLAMA_SERVER}")
    print(f"egpu-alive:   {EGPU_ALIVE_BIN}")
    print("Ctrl+C zum Beenden\n")

    httpd = http.server.HTTPServer(("localhost", LAUNCHER_PORT), Handler)

    def open_browser():
        import time

        time.sleep(0.8)
        webbrowser.open(f"http://localhost:{LAUNCHER_PORT}")

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nBeende...")
        global server_process, egpu_process
        if server_process and server_process.poll() is None:
            server_process.terminate()
        if egpu_process and egpu_process.poll() is None:
            egpu_process.terminate()
        httpd.server_close()


if __name__ == "__main__":
    main()
