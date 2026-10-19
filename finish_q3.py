"""Update and render the notebook's planar compositing examples."""
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
cell = notebook["cells"][13]
functions = "".join(cell["source"]).split('IMAGE_DIR = Path("images")')[0]
examples = '''# Set True to choose your own corners: TL, TR, BR, BL.
# Press R to restart, Enter to confirm, or Esc to cancel.
SELECT_POINTS = False
OUTPUT_DIR = Path("outputs/q3")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

pairs = [
    ("Wadham courtyard", "wadham.jpg", "flag.png",
     [[145, 205], [395, 239], [395, 425], [140, 410]], 0.9, "wadham"),
    ("Sri Lankan flag on bus", "bus.jpg", "sri_lanka_flag.png",
     [[350, 288], [490, 286], [490, 334], [350, 344]], 0.95, "bus"),
]

for title, background_name, source_name, corners, alpha, stem in pairs:
    background = read_image(IMAGE_DIR / background_name)
    source = read_image(IMAGE_DIR / source_name)
    if SELECT_POINTS:
        print(f"Select corners on {title}: TL, TR, BR, BL.")
        destination_points = select_four_points(background, title)
    else:
        destination_points = np.asarray(corners, dtype=np.float32)

    H, warped, result = apply_homography(
        background, source, destination_points, alpha=alpha
    )
    print(f"{title} homography matrix:")
    print(H)
    np.savetxt(OUTPUT_DIR / f"{stem}_homography.txt", H)
    cv.imwrite(str(OUTPUT_DIR / f"{stem}_warped.png"), warped)
    cv.imwrite(str(OUTPUT_DIR / f"{stem}_blended.png"), result)

    fig, axes = plt.subplots(1, 3, figsize=(16, 6), constrained_layout=False)
    for ax, image, image_title in zip(
        axes, [background, warped, result],
        ["Original Background", "Warped Image", "Final Blended Result"]
    ):
        show_image(ax, image, image_title)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / f"{stem}_comparison.png", dpi=150)
    plt.show()
'''
cell["source"] = (functions + examples).splitlines(keepends=True)
notebook["cells"][11]["source"] = [
    "## 3. Planar image compositing\n", "\n",
    "A homography maps the source corners onto a planar quadrilateral. "
    "The warped mask limits alpha blending to that region.\n", "\n",
    "The examples place the Union Jack on the courtyard and the Sri Lankan "
    "flag on the bus. Saved corners make the results reproducible. Set "
    "`SELECT_POINTS = True` to select corners manually in clockwise order "
    "(top-left, top-right, bottom-right, bottom-left).\n"
]
namespace = {}
exec("".join(notebook["cells"][1]["source"]), namespace)
exec("".join(notebook["cells"][12]["source"]), namespace)
outputs = []
buffer = io.StringIO()
def capture_show():
    text = buffer.getvalue()
    if text:
        outputs.append({"output_type": "stream", "name": "stdout", "text": text.splitlines(keepends=True)})
        buffer.seek(0)
        buffer.truncate(0)
    image = io.BytesIO()
    plt.gcf().savefig(image, format="png", dpi=110)
    outputs.append({"output_type": "display_data", "metadata": {}, "data": {
        "image/png": base64.b64encode(image.getvalue()).decode("ascii"),
        "text/plain": ["<Figure: original, warped image, and blended result>"]}})
    plt.close()
plt.show = capture_show
with contextlib.redirect_stdout(buffer):
    exec("".join(cell["source"]), namespace)
cell["outputs"] = outputs
cell["execution_count"] = None
path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("Updated Q3 and rendered both image pairs to outputs/q3.")
