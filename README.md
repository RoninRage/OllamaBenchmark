# 🧠 Ollama Benchmark Tool

Ein flexibles Benchmark-Tool zur Auswertung und Visualisierung der Inferenzleistung lokal gehosteter LLMs mit [Ollama](https://ollama.com/).  
Erzeugt einen vollständigen HTML-Report mit Tabelle, optionalem Diagramm und Systeminformationen.

---

## 🚀 Features

- 📊 HTML-Report mit Tabelle und (optionalem) Diagramm
- 🧠 Tokenrate, Evaluierungsdauer, Ladezeit, GPU-Nutzung & Score
- ⚙️ Vollständig parametrierbar via CLI
- ✅ Automatisches Öffnen im Standardbrowser
- 📦 Einsetzbar für lokale und entfernte Ollama-Server

---

## ⚙️ Verwendung

```bash
python ollama_benchmark.py [OPTIONEN]
```

### Beispiel:

```bash
python ollama_benchmark.py \
  --prompt "Was ist ein Dieselmotor?" \
  --output mein_benchmark \
  --timeout 45 \
  --host http://localhost:11434
```

---

## 🧾 Verfügbare Parameter

| Parameter       | Beschreibung                                         | Standardwert                            |
|----------------|------------------------------------------------------|-----------------------------------------|
| `--prompt`      | Prompt-Text, der an das Modell gesendet wird         | `"Was ist der Unterschied ..."`         |
| `--output`      | Dateiname für den HTML-Report (Zeitstempel wird angehängt) | `ollama_benchmark`               |
| `--no-chart`    | Diagrammausgabe im HTML deaktivieren (optional Flag) | (Diagramm wird standardmäßig angezeigt) |
| `--timeout`     | Timeout für den Modellaufruf (in Sekunden)           | `60`                                    |
| `--host`        | Adresse des Ollama-Servers (lokal oder remote)       | `http://localhost:11434`                |

---

## 📊 HTML-Report enthält:

- ✅ Übersichtstabelle mit:
  - Modellname
  - Anzahl Tokens
  - `eval_duration` (s)
  - `load_duration` (s)
  - Tokenrate (tokens/s)
  - GPU genutzt (✅/❌)
  - Score (Tokenrate pro Sekunde Rechenzeit)
- 📈 Optionales Balkendiagramm (Chart.js)
- 🖥️ Systeminformationen:
  - Betriebssystem, Python-Version, GPU, Ollama-Version

---

## 📂 Ausgabe

Die HTML-Datei wird im aktuellen Verzeichnis gespeichert und automatisch im Standardbrowser geöffnet:

```bash
ollama_benchmark_mein_benchmark_2025-05-14_21-22.html
```

---

## 📌 Hinweise

- Das Tool verwendet die Ollama HTTP-API (`/api/generate`), die automatisch durch `ollama run` oder `ollama serve` bereitgestellt wird.
- Die Datei- und Modellnamen werden automatisch mit dem Zeitstempel versehen.
- Das Tool funktioniert unabhängig davon, ob die Modelle CPU- oder GPU-basiert ausgeführt werden.

---

## 📄 Lizenz

MIT License – nutzbar, erweiterbar, frei einsetzbar.
