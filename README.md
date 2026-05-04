


# Vega56/64 Launcher

<div align="center">

![macOS Intel](https://img.shields.io/badge/macOS-Intel_2018--2020-silver?style=flat-square&logo=apple&logoColor=white)
![LLAMA.cpp](https://img.shields.io/badge/LLAMA.cpp-Vulkan-orange?style=flat-square)
![AMD Vega](https://img.shields.io/badge/AMD-RX_Vega_56/64-purple?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![v1.1](https://img.shields.io/badge/Version-1.1-green?style=flat-square)

**Web-basierter Launcher für llama.cpp mit eGPU Support**

</div>

---

## Warum Vega 56/64 Launcher?

Wenn du eine AMD RX Vega 56 oder 64 hast und damit lokal große Sprachmodelle (LLMs) laufen lassen willst, bist du hier richtig. Dieser Launcher macht es dir leicht:

* Modelle per WebUI auswählen und starten
* Automatische Vulkan-Beschleunigung
* eGPU-Unterstützung für unterbrechungsfreie Inference
* Integrierter Chat – oder nutze den nativen llama-server
* MCP Support für Model Context Protocol
* Jinja für Tool-Use / Function Calling

---

### Warum noch 2026? – Potenzial ausschöpfen statt wegwerfen

Der Launcher entstand mit einem klaren Ziel: **ältere Intel Macs und eGPU-Setups sinnvoll weiterzunutzen** – auch und gerade in 2026.

Apple hat Intel Macs längst abgeschrieben. Aber mit einer Vega 56/64 an einem Thunderbolt-eGPU-Gehäuse (z. B. Razer Core X) wird aus einem "veralteten" Mac mini oder MacBook Pro eine vollwertige, lokale LLM-Inference-Maschine. Kein Cloud-Abo, keine geteilten Ressourcen, volle Datenkontrolle.

---

### Warum ist die Vega so gut für LLM-Inferenz geeignet?

Die Vega 56/64 ist keine "Gaming-GPU" mehr – aber als Inference-Engine ist sie überraschend konkurrenzfähig. Der Grund liegt in der Architektur:

**Speicherbandbreite ist der Flaschenhals bei Inferenz, nicht Rechenleistung.**

Bei jedem generierten Token müssen die kompletten Modellgewichte durch den Speicherbus geladen werden. Das bedeutet: GB/s zählen direkt, TFLOPS kaum.

Hier glänzt die Vega mit ihrem **HBM2-Speicher** (High Bandwidth Memory):

| Merkmal | Vega 56 | Bedeutung für LLMs |
|---|---|---|
| Speichertyp | HBM2 | Extrem hohe Bandbreite |
| Bandbreite | **~410 GB/s** | Schnelle Token-Generierung |
| VRAM | **8 GB** | Qwen3.5-9B-Q5_K_M passt komplett rein |

Zum Vergleich: Eine RTX 3070 mit GDDR6 kommt auf ~448 GB/s – die Vega 56 ist also auf Augenhöhe mit einer deutlich neueren Gaming-GPU, wenn es um reine Inferenz-Geschwindigkeit geht.

**Kurz:** Die Vega 56/64 ist eine der wenigen älteren GPUs, bei der sich der Weiterbetrieb für lokale LLMs wirklich lohnt – und dieser Launcher macht genau das so einfach wie möglich.

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

> > **⚠️ Thermische Warnung**: Vega 56/64 erreicht bei Vollast (besonders unter Linux) Junction-Temps von **110°C**. Dies kann zu Abstürzen führen. egpu-alive verlängert die Zeit, aber das Problem bleibt bestehen.Alternativ: GPU Layers reduzieren oder bessere Kühlung sicherstellen.

> **Lösung unter Linux**: Das Powerlimit auf **145 Watt** reduzieren (z.B. via LACT TOOL`). Dies sorgt für stabile Laufzeiten bei gleichzeitig guter Performance. Da ich das am Mac nicht mehr testen kann, müsstet Ihr mal suchen ob es mittlerweile eine alternatives Tool vür Mac Os Intel existiert.  Alternativ: GPU Layers reduzieren oder bessere Kühlung sicherstellen.


---

## Quick Start

### 1. Voraussetzungen

- **Mac OS Intel mit AMD Vega 56/64** (aktuell) **ODER** macOS mit AMD eGPU
- [llama.cpp](https://github.com/ggml-org/llama.cpp) **b9010+** (gebaut mit `cmake -DGGML_VULKAN=ON ..`)
- **egpu-alive** – **Bereits kompiliert im Projektordner!** (macOS Binary: `./egpu-alive`)
- Python 3.10+

### 2. Installation

```bash
# Repository klonen
git clone https://github.com/bagueDev/Vega56-64-MacOs-LLAMA.CPP-Launcher.git
cd Vega56-64-MacOs-LLAMA.CPP-Launcher

# Oder einfach start_last.py direkt nutzen
python3 start_last.py
```

### 3. llama.cpp herunterladen & kompilieren (Empfohlen: b9010)

```bash
# Repository klonen
git clone https://github.com/ggml-org/llama.cpp.git ~/llama.cpp
cd ~/llama.cpp

# Neueste Version (b9010) auswählen
git fetch --tags
git checkout b9010

# Kompilieren mit Vulkan-Support
mkdir -p build && cd build
cmake -DGGML_VULKAN=ON ..
make -j$(nproc)  # Linux: nproc, macOS: sysctl -n hw.ncpu
```

> **Ergebnis**: `~/llama.cpp/build/bin/llama-server` ist jetzt bereit.

### 4. egpu-alive erstellen (macOS)

**Swift-Datei anlegen:**
```bash
cat > ~/egpu-alive.swift << 'EOF'
import Cocoa
import Metal
import MetalKit

class AppDelegate: NSObject, NSApplicationDelegate {
    var window: NSWindow!
    var mtkView: MTKView!

    func applicationDidFinishLaunching(_ notification: Notification) {
        var vegaDevice: MTLDevice?
        for device in MTLCopyAllDevices() {
            if device.isRemovable { vegaDevice = device; break }
        }
        guard let device = vegaDevice else { print("Keine eGPU!"); return }
        print("Nutze: \(device.name)")
        window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1, height: 1),
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        mtkView = MTKView(frame: window.contentRect(forFrameRect: window.frame), device: device)
        mtkView.clearColor = MTLClearColor(red: 0, green: 0, blue: 0, alpha: 1)
        mtkView.isPaused = false
        mtkView.enableSetNeedsDisplay = false
        mtkView.preferredFramesPerSecond = 1
        window.contentView = mtkView
        window.orderFront(nil)
    }
}
let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
EOF
```

**Kompilieren:**
```bash
swiftc ~/egpu-alive.swift -framework Cocoa -framework Metal -framework MetalKit -o ~/egpu-alive
```

**Erwartete Ausgabe nach dem Start:**
```
Nutze: AMD Radeon RX Vega 56
```
Wenn `AMD Radeon RX Vega 56` erscheint, ist die eGPU aktiv und wird gehalten.


> ## egpu-alive – Was macht das?

egpu-alive ist ein Hilfsprogramm für macOS/Linux, das verhindert, dass **eGPUs während der Nutzung getrennt werden**:

- **Heartbeat/Timer**: Sendet regelmäßige Signale an die eGPU
- **Verhindert Sleep/Idle**: Hält die eGPU aktiv
- **Überwacht Verbindung**: Prüft, ob die eGPU noch erreichbar ist

> **Wichtig für Vega 56/64**: eGPU-Verbindungen können bei Vollast abbrechen. egpu-alive hält die Verbindung aktiv. Ohne es: Risiko von Disconnects. Mit es: Stabile Inference.

**Im Projektordner bereits enthalten:**
- ✅ `egpu-alive` – Kompilierte Binary (macOS Swift)
- ✅ `egpu-alive.swift` – Quellcode
- 

**Nutzung:**
```bash
# macOS (Binary ist bereits im Ordner)
cd /Verzeichnis
./egpu-alive &

# Oder via Launcher-Button: "▶ egpu-alive starten"
```


### 5. Konfiguration

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
---
<img width="985" height="525" alt="Bildschirmfoto 2026-05-04 um 00 30 34" src="https://github.com/user-attachments/assets/29b6c998-bffb-4134-ae33-ddd5a6244ece" />

---
## Modell-Verzeichnisse hinzufügen

1. Im Launcher: Pfad eingeben (z.B. `/home/user/AI_Models`)
2. Auf **"+ Hinzufügen"** klicken
3. Modelle werden automatisch geladen

---
---


<img width="1107" height="1140" alt="Bildschirmfoto 2026-03-09 um 23 02 32" src="https://github.com/user-attachments/assets/0d60d06f-ae2c-4d6f-982e-269f69d3f383" />


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


### 🦙 Llama-Server & nativer Chat

Neben dem Chat-Button gibt es jetzt einen **"🦙 Llama"-Button**:

* Öffnet den nativen llama-server Chat in neuem Tab
- Direkter Zugriff auf `http://localhost:8080`

---

### 💾 Chat-Verlauf & Speicherung

Deine Gespräche gehen nicht verloren:

* Chats werden automatisch lokal gespeichert
* Verlauf bleibt auch nach Browser-Reload erhalten
* Kein Account, kein Cloud-Sync – alles bleibt auf deiner Maschine

---

### 🔌 MCP Server – direkt im Launcher

Der Launcher unterstützt das **Model Context Protocol (MCP)** – du kannst MCP-Server direkt einbinden und nutzen:

* Verbinde Tools, APIs oder lokale Dienste per MCP
* Der Launcher erkennt laufende MCP-Server automatisch
* Ideal für Tool-Use und Function Calling in Kombination mit Jinja-Templates
* Erweitert den Chat um echte Werkzeuge – Dateizugriff, Websuche, eigene Scripts und mehr

MCP macht aus dem einfachen Chat-Interface einen vollwertigen lokalen AI-Agenten – ganz ohne Cloud.

### 📊 Kontext-Anzeige korrigiert
- Zeigt jetzt den tatsächlichen Kontext-Wert aus dem Modell
- Aktualisiert sich während des Streamings (nicht erst am Ende)
- Unterstützt große Kontexte (z.B. 32768)

---
### 🔗 API Integration

Du kannst den llama-server auch mit anderen Tools nutzen – er spricht die OpenAI-kompatible API:

```
http://localhost:8080/v1
```

---

### 💻 VS Code + Continue Plugin – lokales Agentic Coding

Ein besonders praktisches Beispiel: **Continue** (VS Code Extension) direkt mit deinem lokalen llama-server verbinden und damit agentenbasiert coden – komplett offline, komplett privat.

#### Empfohlene Modelle

Aus eigener Erfahrung funktionieren diese beiden besonders gut:

| Modell | Stärken |
|---|---|
| `Qwen3.5-9B-Q5_K_M.gguf` | Stark bei Code, Tool-Use, strukturierten Aufgaben |
| `Gemma-4-E4B-Q5_K_M.gguf` | Schnell, präzise, sehr gute Instruction-Following |

> 📺 Gemma 4 haben wir auf unserem YouTube-Kanal **[bague2010](https://www.youtube.com/@bague2010)** ausführlich getestet – schau rein:
> **[➜ Gemma 4 auf der Vega 56 – lokaler LLM Test](https://youtu.be/a9Rx96HdJog?si=I1m9zP_9Aj-GGkOa)**

#### Setup in Continue (`~/.continue/config.yaml`):

```yaml
models:
  - name: Vega56 Qwen3.5-9B
    provider: openai
    model: Qwen3.5-9B-Q5_K_M
    apiBase: http://localhost:8080/v1
    apiKey: none
    roles:
      - chat
      - edit
      - apply
    maxTokens: 8192

  - name: Vega56 Gemma-4-E4B
    provider: openai
    model: Gemma-4-E4B-Q5_K_M
    apiBase: http://localhost:8080/v1
    apiKey: none
    roles:
      - chat
      - edit
      - apply
    maxTokens: 8192
```

#### Was du damit machen kannst:

* **Tab-Completion** – Qwen3 vervollständigt deinen Code direkt im Editor
* **Chat im Editor** – Fragen stellen, Refactoring, Erklärungen – alles lokal
* **Agentic Mode** – Continue bearbeitet mehrere Dateien auf einmal, führt Änderungen durch, schlägt Fixes vor
* **Codebase-Kontext** – Continue indiziert dein Projekt und gibt dem Modell relevanten Kontext

---

### 🎯 Wie gut funktioniert das?

Ehrlich gesagt: **gut** – mit realistischen Erwartungen.

Für **kleinere Projekte** läuft es richtig flott und macht echten Spaß. Gemma-4-E4B-Q5_K_M versteht Kontext, schreibt sauberen Code und korrigiert Fehler zuverlässig. Mit etwas **Kreativität beim Prompten** und dem richtigen Workflow kann man aber auch bei größeren Projekten erstaunlich viel erreichen – man muss nur ein bisschen experimentieren.

Und das Beste: **Es ist alles lokal und privat.** Kein Code verlässt deine Maschine. Kein API-Abo, keine Rate Limits, kein Datenschutzproblem. Deine Projekte bleiben deine Projekte.

> 💡 **Tipp:** Für beste Ergebnisse in Continue die Modelle mit `--jinja` starten (ist im Launcher bereits als Option verfügbar) – das aktiviert korrektes Chat-Template-Handling und verbessert Tool-Use bei beiden Modellen spürbar.


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

### 📖 Weiterführende Dokumentation

Für die vollständige Einrichtung – Vulkan-Kompilierung, llama.cpp Build-Optionen und Konfigurationsreferenz – bitte unbedingt auch das Handbuch lesen:

➜ **Vega56 LLM – Handbuch & Konfigurationsreferenz**

> Enthält: Vulkan-Build auf macOS Intel, llama.cpp Flags, eGPU-Setup, empfohlene Startparameter und mehr.
---
<img width="2538" height="1306" alt="Bildschirmfoto 2026-03-09 um 23 02 56" src="https://github.com/user-attachments/assets/dfb5039a-e287-46a1-94ab-5b72243e9f67" />



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
│  │Gemma-4-E4B-Q5_K_M      x.x GB   │   │
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
