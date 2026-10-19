import json
from pathlib import Path

path = Path('getting_started.ipynb')
nb = json.loads(path.read_text(encoding='utf-8'))
cell = nb['cells'][15]
source = ''.join(cell['source'])
source = source.replace('["AAAA1.jpg", "AECC2.jpg", "ADAD1.jpg", "AECC3.jpg", "AECC4.jpg"]',
                        '["AAAA1.jpg", "ADAD1.jpg", "AECC2.jpg", "AECC3.jpg", "AECC4.jpg"]')
source = source.replace('figsize=(18, 8)', 'figsize=(12, 5.6)')
source = '\n'.join('    ax.set_title(f"RANSAC matches - {pcb_names[i]}", fontsize=8)' if 'ax.set_title(f"RANSAC Feature Matches' in line else line for line in source.split('\n'))
source = source.replace('    matched_image = cv.drawMatches(', '''    # Show at most 25 evenly spaced inliers to keep the lines readable.
    inlier_ids = np.flatnonzero(inlier_mask_list[i].ravel())
    selected = inlier_ids[np.linspace(0, len(inlier_ids) - 1,
                                    min(25, len(inlier_ids)), dtype=int)]
    display_mask = np.zeros(len(good_matches[i]), dtype=np.uint8)
    display_mask[selected] = 1
    matched_image = cv.drawMatches(''')
source = source.replace('matchesMask=inlier_mask_list[i].ravel().tolist()', 'matchesMask=display_mask.tolist()')
source = source.replace('fig.tight_layout()', 'fig.tight_layout(pad=0.5, h_pad=1.2, w_pad=0.5)')
cell['source'] = source.splitlines(keepends=True)
cell = nb['cells'][16]
source = ''.join(cell['source']).split('for i, name in enumerate(pcb_names):')[0]
source = source.replace('binary_difference_images = []', 'binary_difference_images = []\nvalid_masks = []')
source = source.replace('        aligned_images.append(None)', '        valid_masks.append(None)\n        aligned_images.append(None)')
source = source.replace('    aligned_images.append(aligned)', '    valid_masks.append(valid_mask)\n    aligned_images.append(aligned)')
source += '''# One compact comparison grid, with one row per PCB image.
fig, axes = plt.subplots(len(pcb_names), 4, figsize=(8, 11),
                         constrained_layout=False)
for i, name in enumerate(pcb_names):
    for ax in axes[i]:
        ax.axis("off")
    if aligned_images[i] is None:
        axes[i, 0].text(0.5, 0.5, f"{name}: alignment failed", ha="center")
        continue
    axes[i, 0].imshow(cv.cvtColor(im_list[i], cv.COLOR_BGR2RGB))
    axes[i, 1].imshow(cv.cvtColor(aligned_images[i], cv.COLOR_BGR2RGB))
    axes[i, 2].imshow(difference_images[i], cmap="gray", vmin=0, vmax=255)
    axes[i, 3].imshow(valid_masks[i], cmap="gray", vmin=0, vmax=255)
    for ax, title in zip(axes[i], ["Original PCB", "Aligned PCB",
                                   "Absolute Difference", "Valid Area (white)"]):
        ax.set_title(title, fontsize=6, pad=3)
    axes[i, 1].text(1.05, 1.12, f"PCB image - {name}",
                    transform=axes[i, 1].transAxes, ha="center", fontsize=7)
fig.tight_layout(pad=0.5, h_pad=1.6, w_pad=0.6)
plt.show()
'''
cell['source'] = source.splitlines(keepends=True)
for cell in nb['cells'][15:17]:
    cell['outputs'] = []
    cell['execution_count'] = None
path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
