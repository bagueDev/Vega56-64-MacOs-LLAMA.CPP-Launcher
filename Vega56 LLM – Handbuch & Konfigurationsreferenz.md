Vega56-LLM-Handbuch.md

---

# **Vega56 LLM – Handbuch & Konfigurationsreferenz**  
**Mac mini 2018 (Intel i7)  |  AMD RX Vega 56 eGPU  |  llama.cpp Vulkan**

---

## **1. Systemübersicht**

Dieses Setup ermöglicht lokale KI‑Inference auf einem **Mac mini 2018** mit einer **AMD RX Vega 56 eGPU**.  
Da macOS AMD‑GPUs nicht nativ über Metal für Compute freigibt, wird **llama.cpp mit Vulkan‑Backend** und **MoltenVK** als Übersetzungsschicht verwendet.

| Komponente | Beschreibung |
|-----------|--------------|
| **Rechner** | Mac mini 2018, Intel Core i7 (6C/12T), 32 GB RAM |
| **eGPU** | AMD Radeon RX Vega 56, 8 GB HBM2 |
| **Verbindung** | Thunderbolt 3 (PCIe x16) |
| **macOS** | Sequoia 15.7.4 (24G517)
| **llama.cpp** | Kompiliert mit `GGML_VULKAN=ON`, `GGML_METAL=OFF` |
| **MoltenVK** | v1.4+ via Homebrew |
| **Launcher** | `llama-launcher.py` (Python 3, keine Dependencies) |

**Warum nicht Metal?**  
macOS erlaubt eGPUs keinen direkten Metal‑Compute‑Zugriff für Drittanbieter‑Apps.  
Vulkan → MoltenVK umgeht diese Einschränkung.

---

## **2. Installation & Ersteinrichtung**

### **2.1 Abhängigkeiten installieren**

```bash
brew install libomp vulkan-headers glslang molten-vk shaderc vulkan-loader
```

---

### **2.2  llama.cpp herunterladen & kompilieren (Empfohlen: b9010)

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
---

### **2.3 Vulkan‑Verbindung prüfen**

```bash
./build/bin/llama-cli --list-devices
```

Erwartete Ausgabe:

```
ggml_vulkan: 0 = AMD Radeon RX Vega 56 (MoltenVK) | uma: 0 | fp16: 1
ggml_vulkan: 1 = Intel(R) UHD Graphics 630 (MoltenVK) | uma: 1 | fp16: 1
```

---

## **3. Launcher verwenden**

### **3.1 Starten**

```bash
python3 ~/llama-launcher.py
```

Browser öffnet sich automatisch:  
**http://localhost:9999**

---

### **3.2 Workflow**

- Modell auswählen (alle `.gguf` im Ordner werden erkannt)
- Parameter anpassen (Kontext, GPU‑Layers, Threads, Port)
- **Starten** → gelb (lädt) → grün (bereit)
- **Chat** öffnen
- Beenden: Stop → Terminal `Ctrl+C`

---

### **3.3 Chat‑Oberfläche**

- Enter = senden  
- Shift+Enter = Zeilenumbruch  
- System Prompt optional  
- Token‑Monitor live  
- Continue.dev‑Snippet  
- Verlauf löschen

---

## **4. Parameter‑Referenz**

| Parameter | Standard | Erklärung |
|----------|----------|-----------|
| **-ngl** | 99 | GPU‑Layers. 99 = alles auf GPU. |
| **--device** | Vulkan0 | Vulkan‑Device auswählen (Vega 56 = Vulkan0). |
| **--ctx-size** | 4096 | Kontextlänge in Tokens. |
| **--threads** | 6 | CPU‑Threads für Non‑GPU‑Tasks. |
| **--port** | 8080 | API‑Port. |
| **--host** | 0.0.0.0 | Netzwerk‑Interface. |
| **--batch-size** | 512 | Prompt‑Batchgröße. |

---

### **4.1 GPU Layers (-ngl) im Detail**

| Einstellung | Bedeutung |
|------------|-----------|
| **-ngl 99** | Alle Schichten auf GPU. Empfohlen. |
| **-ngl 0** | CPU‑Modus. Sehr langsam. |
| **-ngl 32** | Hybrid‑Modus für große Modelle. |

**VRAM‑Faustregel:**  
- 8B Q4 → ~4.5 GB  
- 14B Q4 → ~8.5 GB (passt nicht vollständig)

---

### **4.2 Kontextgröße (--ctx-size)**

| Tokens | Wörter | VRAM |
|--------|--------|-------|
| 2048 | ~1500 | niedrig |
| 4096 | ~3000 | mittel |
| 8192 | ~6000 | ~7 GB |
| 16384 | ~12000 | zu groß für Vega 56 |

---

## **5. Modelle**

### **5.1 Vorhandene Modelle**

| Modell | Größe | Speed | Empfehlung |
|--------|--------|--------|------------|
| **Qwen3‑8B‑Q4_K_M** | ~4.5 GB | ~25 tok/s | ⭐ Beste Wahl |
| Qwen3‑8B‑Q5_K_M | ~5.5 GB | etwas langsamer | höhere Qualität |
| Llama‑3‑8B‑Instruct | ähnlich | gut | Alternative |
| Phi‑3‑mini‑128k | klein | ~40 tok/s | schnell, weniger präzise |

---

### **5.2 Quantisierungen**

| Quant | Bits | Qualität | VRAM |
|-------|------|----------|-------|
| Q2_K | 2 | niedrig | sehr klein |
| **Q4_K_M** | 4 | gut | optimal |
| Q5_K_M | 5 | höher | passt |
| Q6_K | 6 | sehr gut | eng |
| Q8_0 | 8 | fast verlustfrei | zu groß |
| F16 | 16 | unkomprimiert | riesig |

---

## **6. Continue.dev in VSCode**

### **6.1 Installation**

- VSCode öffnen  
- Extensions → „Continue“ installieren  

---

### **6.2 Konfiguration**

`~/.continue/config.yaml`:

```yaml
- name: Vega56 Qwen3-8B
  provider: openai
  model: local
  apiBase: http://localhost:8080/v1
  apiKey: none
  roles:
    - chat
    - edit
    - apply
  maxTokens: 4096
```

---

### **6.3 Verwendung**

- Cmd+L → Chat  
- Modell auswählen  
- Code markieren → Cmd+L  
- Cmd+I → Inline‑Edit  

---

## **7. Performance & Optimierung**

### **7.1 Gemessene Werte**

| Modell | Speed |
|--------|--------|
| Qwen3‑8B Q4 | ~25 tok/s |
| Phi‑3‑mini | ~40 tok/s |
| CPU‑Modus | ~3–5 tok/s |

---

### **7.2 Tipps**

- Kontext reduzieren  
- Batch‑Size erhöhen  
- eGPU vor dem Boot anschließen  
- Keine GPU‑Apps parallel  
- Kleinere Modelle für Autocomplete  

---

## **8. Fehlerbehebung**

### **8.1 Häufige Probleme**

| Problem | Lösung |
|---------|--------|
| Modell lädt nicht | SSD‑Pfad prüfen |
| Nur CPU erkannt | eGPU beim Boot angeschlossen? |
| Server startet nicht | Port prüfen |
| macOS Warnung | `xattr -dr com.apple.quarantine` |
| Chat verbindet nicht | Warten bis grün |
| Langsam | `--list-devices` prüfen |

---

### **8.2 Diagnosebefehle**

```bash
system_profiler SPDisplaysDataType | grep -A5 'Vega 56'
./build/bin/llama-cli --list-devices
otool -L ./build/bin/llama-cli | grep -E 'vulkan|molten'
lsof -i :8080
```

---

## **9. Nützliche Terminal‑Aliase**

In `~/.zshrc`:

```bash
alias llm='python3 ~/llama-launcher.py'

alias llm-qwen='cd ~/llama.cpp && ./build/bin/llama-server \
  -m /AIModells/LLM/GGUF/Qwen3-8B-Q4_K_M.gguf \
  -ngl 99 --device Vulkan0 --ctx-size 4096 --port 8080'

alias llm-update='cd ~/llama.cpp && git pull && \
  cmake -B build -DGGML_METAL=OFF -DGGML_VULKAN=ON && \
  cmake --build build --config Release'
```

Aktivieren:

```bash
source ~/.zshrc
```

---

## **10. Schnellreferenz**

| Funktion | Befehl |
|----------|--------|
| Launcher starten | `python3 ~/Vega.py` |
| Browser | http://localhost:9999 |
| API | http://localhost:8080/v1 |
| Modelle | `//` |
| llama.cpp | `~/llama.cpp/` |
| Continue Config | `~/.continue/config.yaml` |
| Empfohlenes Modell | Gemma 4 E4B |
| GPU‑Parameter | `-ngl 99 --device Vulkan0` |
| Kontext | `--ctx-size 4096` |

---
**Viel Spaß mit lokalen LLMs! 🤖**

---

*Entwickelt von [bagueDev](https://github.com/bagueDev/Vega56-64-MacOs-LLAMA.CPP-Launcher) · [YouTube](https://youtube.com/@bague2010) · [GitHub](https://github.com/bagueDev)*

</div>


---
