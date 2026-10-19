"""Export saved notebook cells to printable HTML without rerunning them."""
import html
import json
import re
from pathlib import Path
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer

root = Path(__file__).resolve().parent
notebook = json.loads((root / "getting_started.ipynb").read_text(encoding="utf-8"))
formatter = HtmlFormatter()
parts = []
for cell in notebook["cells"]:
    source = "".join(cell.get("source", []))
    if cell["cell_type"] == "markdown":
        text = html.escape(source)
        text = re.sub(r"(?m)^(#{1,6}) (.+)$", lambda m: f"<h{len(m[1])}>{m[2]}</h{len(m[1])}>", text)
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
        parts.append('<section class="markdown">' + text.replace("\n", "<br>\n") + '</section>')
    elif cell["cell_type"] == "code":
        parts.append(highlight(source, PythonLexer(), formatter))
        for output in cell.get("outputs", []):
            data = output.get("data", {})
            if "image/png" in data:
                encoded = data["image/png"]
                if isinstance(encoded, list):
                    encoded = "".join(encoded)
                parts.append(f'<div class="figure"><img src="data:image/png;base64,{encoded}"></div>')
            elif "text/html" in data:
                parts.append('<div class="table">' + "".join(data["text/html"]) + '</div>')
            else:
                text = output.get("text", data.get("text/plain", []))
                if text:
                    parts.append('<pre class="output">' + html.escape("".join(text)) + '</pre>')
css = '''
@page { size: A4; margin: 15mm 12mm; }
body { font: 10pt Arial, sans-serif; color: #222; }
h1 { font-size: 19pt; } h2 { font-size: 15pt; break-after: avoid; }
.markdown { margin: 12px 0; line-height: 1.4; }
.highlight { background: #f7f7f7; padding: 8px; margin: 10px 0; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; font: 8pt Consolas, monospace; }
.figure { text-align: center; break-inside: avoid; margin: 12px 0; }
img { max-width: 100%; max-height: 245mm; object-fit: contain; }
table { border-collapse: collapse; font-size: 8pt; max-width: 100%; }
td, th { padding: 4px; border: 1px solid #ddd; }
''' + formatter.get_style_defs('.highlight')
target = root / "getting_started.html"
target.write_text('<!doctype html><html><head><meta charset="utf-8"><title>Fitting and Alignment</title><style>' + css + '</style></head><body>' + "\n".join(parts) + '</body></html>', encoding="utf-8")
print(target)
