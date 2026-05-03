<img width="1383" height="730" alt="Bildschirmfoto 2026-03-09 um 23 02 18" src="https://github.com/user-attachments/assets/2a36500f-37b5-4545-8da6-81c2a97193bd" /># Vega56/64 Launcher

# Vega56/64 Launcher

<div align="center">

![LLAMA.cpp](https://img.shields.io/badge/LLAMA.cpp-Vulkan-orange?style=flat-square)
![AMD Vega](https://img.shields.io/badge/AMD-RX_Vega_56/64-purple?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![v1.1](https://img.shields.io/badge/Version-1.1-green?style=flat-square)

**Web-basierter Launcher für llama.cpp mit eGPU Support**

</div>

---

## Warum Vega56/64 Launcher?

Wenn du eine **AMD RX Vega 56 oder 64** hast und damit lokal große Sprachmodelle (LLMs) laufen lassen willst, bist du hier richtig. Dieser Launcher macht es dir leicht:

- Modelle per WebUI auswählen und starten
- Automatische Vulkan-Beschleunigung
- eGPU-Unterstützung für unterbrechungsfreie Inference
- Integrierter Chat – oder nutze den nativen llama-server
- **MCP Support** für Model Context Protocol
- **Jinja** für Tool-Use / Function Calling

> **TL;DR**: Keine Kommandozeile nötig. Modell auswählen → Starten → Chatten.

---

## Features

| Feature | Beschreibung |
|---------|--------------|
| 🚀 **Vulkan Acceleration** | Nutzt AMD Vega GPU für schnelle Inference |
| 🔥 **eGPU Support** | Integriert mit `egpu-alive` für stabile eGPU-Verbindung |
| 🌐 **Web UI** | Modell-Auswahl, Konfiguration, Server-Status – alles im Browser |
| 💬 **Integrierter Chat** | Chatte direkt im Browser mit deinem Modell |
| 🦙 **Native UI** | Alternativ: Öffne den original llama-server Chat |
| 📊 **Token Monitor** | Sieh Tokens/s, Kontext-Auslastung & mehr in Echtzeit |
| 💾 **Chat Export** | Exportiere deine Chats als Markdown |
| 🔧 **MCP Support** | Model Context Protocol via `--webui-mcp-proxy` |
| 🛠️ **Tool Use** | Jinja-Templates für Function Calling |

---

## GPU Layers – Was bedeutet das?

Die Anzahl der **GPU Layers** bestimmt, wie viel vom Modell auf der GPU läuft:

| Layers | Modus | Beschreibung |
|--------|-------|--------------|
| **0** | 🔵 CPU Only | Keine GPU-Beschleunigung, alles läuft auf der CPU |
| **1-20** | ⚡ Hybrid | Teile auf GPU, Rest auf CPU. Gut für kleine VRAM |
| **21-35** | 🚀 GPU Optimized | Viel auf GPU. Für 8GB VRAM (Vega 56/64 hat 8GB) |
| **99** | 🎯 Voll GPU | Alles auf der GPU, maximaler Speed |

> **Empfehlung**: Starte mit `20` und erhöhe schrittweise bis `35`. Wenn Out-of-Memory → reduzieren.

> > **⚠️ Thermische Warnung**: Vega 56/64 erreicht bei Vollast Junction-Temps von **110°C**. Dies kann zu Abstürzen führen. egpu-alive verlängert die Zeit, aber das Problem bleibt bestehen.Alternativ: GPU Layers reduzieren oder bessere Kühlung sicherstellen.

> **Lösung unter Linux**: Das Powerlimit auf **145 Watt** reduzieren (z.B. via LACT TOOL`). Dies sorgt für stabile Laufzeiten bei gleichzeitig guter Performance. Da ich das am Mac nicht mehr testen kann, müsstet Ihr mal suchen ob es mittlerweile eine alternatives Tool vür Mac Os Intel existiert.  Alternativ: GPU Layers reduzieren oder bessere Kühlung sicherstellen.


---

## Quick Start

### 1. Voraussetzungen

- **Linux mit AMD Vega 56/64** (aktuell) **ODER** macOS mit AMD eGPU
- [llama.cpp](https://github.com/ggml-org/llama.cpp) **b9010+** (gebaut mit `cmake -DGGML_VULKAN=ON ..`)
- [egpu-alive](https://github.com/leon/mac-egpu) (für eGPU-Stabilität – optional aber empfohlen)
- Python 3.10+

### 2. Installation

```bash
# Repository klonen
git clone https://github.com/bagueDev/Vega56-64-MacOs-LLAMA.CPP-Launcher.git
cd Vega56-64-MacOs-LLAMA.CPP-Launcher

# Oder einfach start_last.py direkt nutzen
python3 start_last.py
```

### 3. llama.cpp Aktualisierung (Empfohlen: b9010)

```bash
cd ~/llama.cpp
git fetch --tags
git checkout b9010
mkdir -p build && cd build
cmake -DGGML_VULKAN=ON ..
make -j$(nproc)  # Linux: nproc, macOS: sysctl -n hw.ncpu
```

### 4. Konfiguration

Bearbeite die Konstanten am Anfang von `start_last.py`:

```python
LLAMA_CPP_DIR   = str(Path.home() / "llama.cpp")
LLAMA_SERVER    = str(Path.home() / "llama.cpp/build/bin/llama-server")
EGPU_ALIVE_BIN  = str(Path.home() / "egpu-alive")
DEFAULT_MODELS  = "/Pfad/zu/deinen/Modellen"
LAUNCHER_PORT   = 9999
SERVER_PORT     = 8080
```

### 5. Starten

```bash
python3 start_last.py
```

Der Browser öffnet sich automatisch auf `http://localhost:9999`.

---

## Modell-Verzeichnisse hinzufügen

1. Im Launcher: Pfad eingeben (z.B. `/home/user/AI_Models`)
2. Auf **"+ Hinzufügen"** klicken
3. Modelle werden automatisch geladen

---

## Chat Template auswählen

Je nach Modell brauchst du unterschiedliche Chat-Templates:

| Template | Modelle |
|----------|---------|
| `auto` | Automatisch aus GGUF-Metadaten (empfohlen) |
| `chatml` | **Qwen3.5 9B** (empfohlen!) |
| `gemma4` | **Gemma 4 E4B** (empfohlen!) |
| `llama3` | Llama 3 / 3.1 / 3.2 |
| `mistral` | Mistral, Mixtral |
| `gemma` | Gemma 2 / 3 |
| `phi3` | Phi-3 / 3.5 |
| `zephyr` | Zephyr |

> **🎯 Empfohlene Modelle** (getestet & stabil auf Vega 56/64):
> - **Qwen3.5 9B** (z.B. `Qwen3.5-9B-Q5_K_M.gguf`) → Template: `chatml`
> - **Gemma 4 E4B** (z.B. `Gemma-4-E4B-Q5_K_M.gguf`) → Template: `gemma4`

---

## Neue Features in v1.1

### 🔧 MCP Support (Model Context Protocol)
Aktiviert durch `--webui-mcp-proxy` Flag. Ermöglicht:
- MCP-Clients mit llama-server verbinden
- Tools und Ressourcen via MCP nutzen
- URL: `http://localhost:8080`

### 🛠️ Tool Use / Function Calling
Aktiviert durch `--jinja` Flag:
- Jinja-Templates für Tool-Calling
- Kompatibel mit Gemma 4, Llama 3, Mistral, etc.

### 🦙 Llama-Button
Neben dem Chat-Button gibt es jetzt einen **"🦙 Llama"** Button:
- Öffnet den nativen llama-server Chat in neuem Tab
- Direkter Zugriff auf `http://localhost:8080`

### 📊 Kontext-Anzeige korrigiert
- Zeigt jetzt den tatsächlichen Kontext-Wert aus dem Modell
- Aktualisiert sich während des Streamings (nicht erst am Ende)
- Unterstützt große Kontexte (z.B. 32768)

---

## API Integration

Du kannst den llama-server auch mit anderen Tools nutzen:

```yaml
# Für Continue.dev, OpenWebUI, etc.
- name: Vega56/64
  provider: openai
  model: <dein-modell>
  apiBase: http://localhost:8080/v1
  apiKey: none
```

---

## egpu-alive – Was macht das?

egpu-alive ist ein Hilfsprogramm für macOS/Linux, das verhindert, dass **eGPUs während der Nutzung getrennt werden**:

- **Heartbeat/Timer**: Sendet regelmäßige Signale an die eGPU
- **Verhindert Sleep/Idle**: Hält die eGPU aktiv
- **Überwacht Verbindung**: Prüft, ob die eGPU noch erreichbar ist

> **Wichtig für Vega 56/64**: eGPU-Verbindungen können bei Volllast abbrechen. egpu-alive hält die Verbindung aktiv. Ohne es: Risiko von Disconnects. Mit es: Stabile Inference.

---

## Troubleshooting

### ❌ "Keine .gguf Dateien gefunden"
→ Modell-Verzeichnis prüfen. Nur `.gguf` Dateien werden geladen.

### ❌ "eGPU getrennt während Inference"
→ `egpu-alive` starten im Launcher (falls eGPU genutzt)

### ❌ "Out of Memory"
→ **GPU Layers reduzieren** (z.B. von 35 auf 20)

### ❌ "Model too large"
→ Quantisiertes Modell nutzen (Q5_K_M, Q4_K_M, etc.)

### ❌ "Gemma 4 läuft nicht"
→ Cache-Typen auf `f16` stellen (automatisch in v1.1)
→ GPU Layers auf 0-20 reduzieren

### ❌ "Junction Temp 110°C / Absturz"
→ **Thermisches Problem!** Vega 56/64 wird bei Volllast sehr heiß
→ GPU Layers reduzieren (weniger Last auf GPU)
→ Bessere Kühlung sicherstellen
→ egpu-alive verlängert die Zeit, aber das Problem bleibt

---

---

<img width="2538" height="1306" alt="Bildschirmfoto 2026-03-09 um 23 02 56" src="https://github.com/user-attachments/assets/dfb5039a-e287-46a1-94ab-5b72243e9f67" />
<img width="1107" height="1140" alt="Bildschirmfoto 2026-03-09 um 23 02 32" src="https://github.com/user-attachments/assets/0d60d06f-ae2c-4d6f-982e-269f69d3f383" />



---

```
┌─────────────────────────────────────────────┐
│  Vega56/64 Launcher                    ⟳   │
├─────────────────────────────────────────────┤
│  Entwickelt von bagueDev                   │
├─────────────────────────────────────────────┤
│  eGPU Status: ● AMD Vega 56/64 aktiv       │
├─────────────────────────────────────────────┤
│  Modell wählen:                             │
│  ┌─────────────────────────────────────┐   │
│  │ Qwen3-8B-Q5_K_M.gguf      4.3 GB   │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Kontext: [32768]  GPU Layers: [20]        │
│  Port: [8080]    Threads: [6]              │
│                                             │
│  [▶ Starten] [■ Stoppen] [Chat →] [🦙 Llama] │
└─────────────────────────────────────────────┘
```

---

## Lizenz

MIT License – frei nutzbar und modifizierbar.

---

## Credits

- [llama.cpp](https://github.com/ggml-org/llama.cpp) – Das Herzstück
- [egpu-alive](https://github.com/leon/mac-egpu) – eGPU Stabilität
- Community für Testing & Feedback ❤️

---

<div align="center">

**Viel Spaß mit lokalen LLMs! 🤖**

---

*Entwickelt von [bagueDev](https://github.com/bagueDev/Vega56-64-MacOs-LLAMA.CPP-Launcher) · [YouTube](https://youtube.com/@bague2010) · [GitHub](https://github.com/bagueDev)*

</div>


---

## Warum Vega56/64 Launcher?

Wenn du eine **AMD RX Vega 56 oder 64** hast und damit lokal große Sprachmodelle (LLMs) laufen lassen willst, bist du hier richtig. Dieser Launcher macht es dir leicht:

- Modelle per WebUI auswählen und starten
- Automatische Vulkan-Beschleunigung
- eGPU-Unterstützung für unterbrechungsfreie Inference
- Integrierter Chat – oder nutze den nativen llama-server

> **TL;DR**: Keine Kommandozeile nötig. Modell auswählen → Starten → Chatten.

---

## Features

| Feature | Beschreibung |
|---------|--------------|
| 🚀 **Vulkan Acceleration** | Nutzt AMD Vega GPU für schnelle Inference |
| 🔥 **eGPU Support** | Integriert mit `egpu-alive` für stabile eGPU-Verbindung |
| 🌐 **Web UI** | Modell-Auswahl, Konfiguration, Server-Status – alles im Browser |
| 💬 **Integrierter Chat** | Chatte direkt im Browser mit deinem Modell |
| 🦙 **Native UI** | Alternativ: Öffne den original llama-server Chat |
| 📊 **Token Monitor** | Sieh Tokens/s, Kontext-Auslastung & mehr in Echtzeit |
| 💾 **Chat Export** | Exportiere deine Chats als Markdown |

---

## GPU Layers – Was bedeutet das?

Die Anzahl der **GPU Layers** bestimmt, wie viel vom Modell auf der GPU läuft:

| Layers | Modus | Beschreibung |
|--------|-------|--------------|
| **0** | 🔵 CPU Only | Keine GPU-Beschleunigung, alles läuft auf der CPU |
| **1-20** | ⚡ Hybrid | Teile auf GPU, Rest auf CPU. Gut für kleine VRAM |
| **21-35** | 🚀 GPU Optimized | Viel auf GPU. Für 8GB VRAM (Vega 56/64 hat 8GB) |
| **99** | 🎯 Voll GPU | Alles auf der GPU, maximaler Speed |

> **Empfehlung**: Starte mit `20` und erhöhe schrittweise bis `35`. Wenn Out-of-Memory → reduzieren.

---

## Quick Start

### 1. Voraussetzungen

- macOS mit AMD eGPU (RX Vega 56/64) **ODER** Linux mit Vega
- [llama.cpp](https://github.com/ggml-org/llama.cpp) gebaut (`llama-server` vorhanden)
- [egpu-alive](https://github.com/le们x/egpu-alive) (für eGPU – optional)
- Python 3.10+

### 2. Installation

```bash
# Repository klonen
git clone https://github.com/dein-repo/vega56-launcher.git
cd vega56-launcher

# Oder einfach start_last.py direkt nutzen
python3 start_last.py
```

### 3. Konfiguration

Bearbeite die Konstanten am Anfang von `start_last.py`:

```python
LLAMA_CPP_DIR   = str(Path.home() / "llama.cpp")
LLAMA_SERVER    = str(Path.home() / "llama.cpp/build/bin/llama-server")
EGPU_ALIVE_BIN  = str(Path.home() / "egpu-alive")
DEFAULT_MODELS  = "/Pfad/zu/deinen/Modellen"
LAUNCHER_PORT   = 9999
SERVER_PORT     = 8080
```

### 4. Starten

```bash
python3 start_last.py
```

Der Browser öffnet sich automatisch auf `http://localhost:9999`.

---

## Modell-Verzeichnisse hinzufügen

1. Im Launcher: Pfad eingeben (z.B. `/Users/name/AI_Models`)
2. Auf **"+ Hinzufügen"** klicken
3. Modelle werden automatisch geladen

---

## Chat Template auswählen

Je nach Modell brauchst du unterschiedliche Chat-Templates:

| Template | Modelle |
|----------|---------|
| `auto` | Automatisch aus GGUF-Metadaten (empfohlen) |
| `chatml` | Qwen3, Qwen2.5 |
| `llama3` | Llama 3 / 3.1 / 3.2 |
| `mistral` | Mistral, Mixtral |
| `gemma` | Gemma 2 / 3 |
| `phi3` | Phi-3 / 3.5 |
| `zephyr` | Zephyr |

---

## API Integration

Du kannst den llama-server auch mit anderen Tools nutzen:

```yaml
# Für Continue.dev, OpenWebUI, etc.
- name: Vega56/64
  provider: openai
  model: <dein-modell>
  apiBase: http://localhost:8080/v1
  apiKey: none
```

---

## Troubleshooting

### ❌ "Keine .gguf Dateien gefunden"
→ Modell-Verzeichnis prüfen. Nur `.gguf` Dateien werden geladen.

### ❌ "eGPU getrennt während Inference"
→ `egpu-alive` starten im Launcher (falls eGPU genutzt)

### ❌ "Out of Memory"
→ **GPU Layers reduzieren** (z.B. von 35 auf 20)

### ❌ "Model too large"
→ Quantisiertes Modell nutzen (Q5_K_M, Q4_K_M, etc.)

---

## Screenshots

```
┌─────────────────────────────────────────────┐
│  Vega56/64 Launcher                    ⟳   │
├─────────────────────────────────────────────┤
│  eGPU Status: ● AMD Vega 56 aktiv          │
├─────────────────────────────────────────────┤
│  Modell wählen:                             │
│  ┌─────────────────────────────────────┐   │
│  │ Qwen3-8B-Q5_K_M.gguf      4.3 GB   │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Kontext: [4096]  GPU Layers: [20]         │
│  Port: [8080]    Threads: [6]              │
│                                             │
│  [▶ Starten] [■ Stoppen] [Chat →] [🦙 Llama] │
└─────────────────────────────────────────────┘
```

---

## Lizenz

MIT License – frei nutzbar und modifizierbar.

---

## Credits

- [llama.cpp](https://github.com/ggml-org/llama.cpp) – Das Herzstück
- [egpu-alive](https://github.com/leon/mac-egpu) – eGPU Stabilität
- Community für Testing & Feedback ❤️

---

<div align="center">

**Viel Spaß mit lokalen LLMs! 🤖**

---

*Entwickelt von [bagueDev](https://github.com/bagueDev/Vega56-64-MacOs-LLAMA.CPP-Launcher) · [YouTube](https://youtube.com/@bague2010) · [GitHub](https://github.com/bagueDev)*

</div>
