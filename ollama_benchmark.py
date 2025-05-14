# -*- coding: utf-8 -*-
import argparse
import platform
import subprocess
import requests
import webbrowser
from datetime import datetime
from pathlib import Path

def get_installed_models(host):
    resp = requests.get(f"{host}/api/tags")
    data = resp.json()
    return [model["name"] for model in data["models"]]

def get_gpu_info():
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"], capture_output=True, text=True)
        return result.stdout.strip().splitlines()[0] if result.returncode == 0 else "Keine NVIDIA-GPU erkannt"
    except FileNotFoundError:
        return "nvidia-smi nicht installiert"

def is_ollama_using_gpu():
    try:
        result = subprocess.run(["nvidia-smi", "--query-compute-apps=pid,process_name", "--format=csv,noheader"], capture_output=True, text=True)
        output = result.stdout.strip().lower()
        return "ollama" in output or "python" in output
    except Exception:
        return False

def get_ollama_info():
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else "Version nicht erkannt"
    except:
        return "Ollama nicht gefunden"

def normalize_ns(value):
    if value < 10_000:
        return round(value, 2)
    s = value / 1e9
    if s < 0.01:
        s = value / 1e6
    elif s > 10000:
        s = value / 1e3
    return round(s, 2)

def get_color(rate):
    if isinstance(rate, (int, float)):
        if rate >= 40:
            return "#d4edda"
        elif rate >= 20:
            return "#fff3cd"
        else:
            return "#f8d7da"
    return "#eeeeee"

def build_sysinfo_html(prompt, timestamp, gpu_info, ollama_info):
    return f"""
<h2>Systeminformationen</h2>
<ul>
    <li><strong>Betriebssystem:</strong> {platform.system()} {platform.release()}</li>
    <li><strong>Version:</strong> {platform.version()}</li>
    <li><strong>Prozessor:</strong> {platform.processor()}</li>
    <li><strong>Python-Version:</strong> {platform.python_version()}</li>
    <li><strong>GPU:</strong> {gpu_info}</li>
    <li><strong>Ollama:</strong> {ollama_info}</li>
    <li><strong>Zeit:</strong> {timestamp}</li>
</ul>
<p>Prompt: <code>{prompt}</code></p>
"""

def main(args):
    parser = argparse.ArgumentParser(description="Ollama Benchmark Tool",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--prompt", type=str, default="Was ist ein Dieselmotor?")
    parser.add_argument("--output", type=str, default="benchmark")
    parser.add_argument("--no-chart", action="store_true")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--host", type=str, default="http://localhost:11434")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    html_filename = f"{args.output}_{timestamp}.html"

    models = get_installed_models(args.host)
    if not models:
        print("❌ Keine Modelle installiert.")
        return

    gpu_info = get_gpu_info()
    ollama_info = get_ollama_info()
    sys_info_html = build_sysinfo_html(args.prompt, timestamp, gpu_info, ollama_info)

    html_head = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Ollama Benchmark Report - {timestamp}</title>
<style>
body {{ font-family: Arial, sans-serif; background: #f9f9f9; color: #333; padding: 2em; }}
table {{ border-collapse: collapse; width: 100%; background: white; margin-bottom: 2em; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
th {{ background: #eee; }}
th.sortable {{ cursor: pointer; }}
th.sortable::after {{ content: " ⬍"; font-size: 0.8em; color: #888; }}
</style>
<script>
document.addEventListener('DOMContentLoaded', () => {{
  document.querySelectorAll("th.sortable").forEach((th, i) => {{
    th.addEventListener("click", () => {{
      const table = th.closest("table");
      const tbody = table.querySelector("tbody");
      const rows = Array.from(tbody.querySelectorAll("tr"));
      const asc = th.classList.toggle("asc");
      rows.sort((a, b) => {{
        const va = a.children[i].innerText;
        const vb = b.children[i].innerText;
        const na = parseFloat(va.replace(",", ".")) || 0;
        const nb = parseFloat(vb.replace(",", ".")) || 0;
        return asc ? na - nb : nb - na;
      }});
      rows.forEach(row => tbody.appendChild(row));
    }});
  }});
}});
</script>
</head>
<body>
<h1>Ollama Benchmark Report</h1>
{sys_info_html}
"""

    html_rows = ""
    model_names = []
    tokenrates = []

    for model in models:
        print(f"==> Benchmark läuft für Modell: {model}")
        try:
            response = requests.post(
                f"{args.host}/api/generate",
                json={"model": model, "prompt": args.prompt, "stream": False},
                timeout=args.timeout
            )
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout bei {model}")
            continue

        if response.status_code != 200:
            print(f"❌ Fehler bei {model}")
            continue

        gpu_now = is_ollama_using_gpu()
        data = response.json()
        tokens = data.get("eval_count", 0)
        eval_s = normalize_ns(data.get("eval_duration", 0))
        load_s = normalize_ns(data.get("load_duration", 0))
        try:
            tokenrate = round(tokens / eval_s, 2)
            score = round(tokenrate / eval_s, 2)
        except:
            tokenrate = 0
            score = 0

        model_names.append(model)
        tokenrates.append(tokenrate)

        row_color = get_color(tokenrate)
        gpu_color = "#d4edda" if gpu_now else "#f8d7da"
        gpu_label = "✅" if gpu_now else "❌"

        html_rows += f"""
<tr>
    <td>{model}</td>
    <td>{tokens}</td>
    <td>{eval_s}</td>
    <td>{load_s}</td>
    <td style="background-color: {row_color}">{tokenrate}</td>
    <td style="background-color: {gpu_color}">{gpu_label}</td>
    <td>{score}</td>
</tr>
"""

    chart_html = "" if args.no_chart else f"""
<h2>Tokenrate pro Modell</h2>
<canvas id="tokenChart" width="800" height="400"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
function drawChart(labels, data) {{
  new Chart(document.getElementById("tokenChart"), {{
    type: 'bar',
    data: {{
      labels: labels,
      datasets: [{{
        label: "Tokenrate (tokens/s)",
        data: data,
        backgroundColor: labels.map(label => '#4e79a7')
      }}]
    }},
    options: {{
      responsive: true,
      indexAxis: 'y',
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{
            label: (ctx) => ctx.raw + ' tokens/s'
          }}
        }}
      }},
      scales: {{
        x: {{ beginAtZero: true, title: {{ display: true, text: "Tokenrate (tokens/s)" }} }},
        y: {{ title: {{ display: true, text: "Modelle" }} }}
      }}
    }}
  }});
}}
drawChart([{','.join(f'"{name}"' for name in model_names)}], [{','.join(str(r) for r in tokenrates)}]);
</script>
"""

    html_table = f"""
<table>
<thead>
<tr>
    <th class="sortable">Modell</th>
    <th class="sortable">Tokens</th>
    <th class="sortable">eval_duration (s)</th>
    <th class="sortable">load_duration (s)</th>
    <th class="sortable">Tokenrate (tokens/s)</th>
    <th class="sortable">GPU genutzt</th>
    <th class="sortable">Score</th>
</tr>
</thead>
<tbody>
{html_rows}
</tbody>
</table>
"""

    html_full = html_head + chart_html + html_table + "</body></html>"
    Path(html_filename).write_text(html_full, encoding="utf-8")
    print(f"✅ HTML-Report gespeichert als: {html_filename}")
    webbrowser.open("file://" + str(Path(html_filename).resolve()))

if __name__ == "__main__":
  parser = argparse.ArgumentParser(...)
  args = parser.parse_args()
  main(args)
