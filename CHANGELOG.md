# Changelog

## [Unreleased]

### Added
- **LICENSE** - MIT License file hinzugefügt (entspricht MIT Badge im README)
- **requirements.txt** - Dokumentation der Python-Abhängigkeiten (Python 3.10+, nur Standardbibliothek)
- **Circular Log Buffer** - `deque(maxlen=500)` für Logs implementiert (verhindert Speicherlecks)
- **Neuer API-Endpoint** - `/api/logs` gibt die letzten 500 Log-Zeilen zurück

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

### Fixed
- **Race Conditions** - Globale Variablen werden jetzt thread-sicher über `with server_lock:` abgefragt/gesetzt
- **Zombie-Prozesse** - Subprocess-Waits haben jetzt Timeout (5s) statt unendlich zu warten

---

## [1.1.0] - 2026-05-03

### Added
- **MCP Support** - `--webui-mcp-proxy` Flag für Model Context Protocol
- **Tool Use** - `--jinja` Flag für Function Calling aktiviert
- **Llama-Button** - Öffnet nativen llama-server Chat in neuem Tab
- **Chat Export** - Markdown-Export für Chat-Verläufe
- **Token Monitor** - Korrekte Kontext-Anzeige aus Modell-Metadaten

### Fixed
- **Kontext-Anzeige** - Aktualisiert sich jetzt während des Streamings
- **Gemma 4 Support** - Cache-Typen automatisch auf `f16` gesetzt
