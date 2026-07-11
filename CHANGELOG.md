# Changelog

## [1.2.0] - 11 Juli 2026

### Added
- **LICENSE** - MIT License file hinzugefügt (entspricht MIT Badge im README)
- **requirements.txt** - Dokumentation der Python-Abhängigkeiten (Python 3.10+, nur Standardbibliothek)
- **Circular Log Buffer** - `deque(maxlen=500)` für Logs implementiert (verhindert Speicherlecks)
- **Neuer API-Endpoint** - `/api/logs` gibt die letzten 500 Log-Zeilen zurück
- **KV Cache Option** - UI Dropdown für Cache-Quantisierung: `q4_0`, `q8_0`, `f16` (default), `f32`
- **Max Tokens** - Konfigurierbare Antwortlänge (256-32768), übergeben an `-n`
- **Extra Flags** - Freies Textfeld für beliebige zusätzliche llama-server Flags
- **Sampling Parameter** - Manuelle Eingabe für `Temperature`, `Top K`, `Repeat Penalty` im Launcher UI
- **Preset Templates** - 3 optimierte Vorlagen: `Code` (temp=0.2, top_k=30, rp=1.15), `Chat` (temp=0.7, top_k=40, rp=1.0), `Kreativ` (temp=1.1, top_k=60, rp=1.0)
- **Sampling im Chat** - Temperature, Top K, Repeat Penalty werden als URL-Params an Chat-Seite übergeben und im API-Request verwendet
- **UI Toggles** - `--jinja` und `--webui-mcp-proxy` sind jetzt als Checkbox-Toggles konfigurierbar (beide default: an)
- **Batch Size** - Konfigurierbare Batch-Größe (`-b`, default: 512, step: 64) und uBatch (`-ub`, default: 512, step: 64)
- **No KV Offload** - `--no-kv-offload` Toggle für CPU-only KV Cache (verhindert GPU-Auslagerung)

### Changed
- **Thread Safety** - `threading.Lock()` für alle globalen States hinzugefügt:
  - `server_process`
  - `egpu_process`
  - `models_dirs`
  - `SERVER_PORT`
- **Subprocess Timeout** - `.wait(timeout=5)` mit Fallback auf `.kill()` bei Timeout:
  - `server_process.terminate()` + `wait(timeout=5)`
  - `egpu_process.terminate()` + proper cleanup
- **Log Handling** - Log-Zeilen werden jetzt im `deque` Puffer gespeichert statt nur an das UI zu senden
- **Flags konfigurierbar** - `--jinja` und `--webui-mcp-proxy` sind jetzt ueber UI-Toggles steuerbar statt hardcoded
- **Kontext Default** - Standard-Kontextgroesse von 4096 auf 16384 erhoeht

### Fixed
- **Race Conditions** - Globale Variablen werden jetzt thread-sicher über `with server_lock:` abgefragt/gesetzt
- **Zombie-Prozesse** - Subprocess-Waits haben jetzt Timeout (5s) statt unendlich zu warten
- **Gemma 4 Cache** - Cache-Typen werden jetzt automatisch auf `f16` erzwungen wenn "gemma" im Modellname vorkommt (verhindert Abstürze bei q4_0/q8_0)
- **--predict Flag** - `max_tokens` wird jetzt korrekt als `-n` an llama-server übergeben

---

## [1.1.0] - 2026-03-09

### Added
- **MCP Support** - `--webui-mcp-proxy` Flag für Model Context Protocol
- **Tool Use** - `--jinja` Flag für Function Calling aktiviert
- **Llama-Button** - Öffnet nativen llama-server Chat in neuem Tab
- **Chat Export** - Markdown-Export für Chat-Verläufe
- **Token Monitor** - Korrekte Kontext-Anzeige aus Modell-Metadaten

### Fixed
- **Kontext-Anzeige** - Aktualisiert sich jetzt während des Streamings
- **Gemma 4 Support** - Cache-Typen automatisch auf `f16` gesetzt
