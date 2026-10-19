"""Run the PCB section and store its figures in the notebook and outputs/q4."""
import base64
import contextlib
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

path = Path("getting_started.ipynb")
notebook = json.loads(path.read_text(encoding="utf-8"))
output_dir = Path("outputs/q4")
output_dir.mkdir(parents=True, exist_ok=True)
namespace = {}
figure_number = 0
for index in (15, 16):
    cell = notebook["cells"][index]
    outputs = []
    buffer = io.StringIO()

    def capture_show():
        global figure_number
        text = buffer.getvalue()
        if text:
            outputs.append({"output_type": "stream", "name": "stdout",
                            "text": text.splitlines(keepends=True)})
            buffer.seek(0)
            buffer.truncate(0)
        figure_number += 1
        figure = plt.gcf()
        figure.savefig(output_dir / f"pcb_{figure_number:02d}.png", dpi=120)
        image = io.BytesIO()
        figure.savefig(image, format="png", dpi=90)
        outputs.append({"output_type": "display_data", "metadata": {}, "data": {
            "image/png": base64.b64encode(image.getvalue()).decode("ascii"),
            "text/plain": ["<Figure: PCB alignment results>"]}})
        plt.close(figure)

    plt.show = capture_show
    with contextlib.redirect_stdout(buffer):
        exec("".join(cell["source"]), namespace)
    for output in outputs:
        if output["output_type"] == "stream":
            print("".join(output["text"]), end="", flush=True)
    cell["outputs"] = outputs
    cell["execution_count"] = None

assert all(H is not None for H in namespace["homography_list"])
assert len(namespace["aligned_images"]) == 5
path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("Saved PCB outputs for all five images.")
