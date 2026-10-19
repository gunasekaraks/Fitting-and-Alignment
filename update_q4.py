"""Add the PCB matching and difference workflow to the notebook."""
import json
from pathlib import Path

code = '''from pathlib import Path
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

# Load the reference and the five PCB images.
PCB_DIR = Path("images") / "pcb"
def read_pcb(name):
    path = PCB_DIR / name
    image = cv.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Cannot read image: {path.resolve()}")
    return image

ref = read_pcb("AECC1.jpg")
pcb_names = ["AAAA1.jpg", "AECC2.jpg", "ADAD1.jpg", "AECC3.jpg", "AECC4.jpg"]
im_list = [read_pcb(name) for name in pcb_names]
gray_ref = cv.cvtColor(ref, cv.COLOR_BGR2GRAY)
gray_im_list = [cv.cvtColor(im, cv.COLOR_BGR2GRAY) for im in im_list]

# SIFT descriptors and two nearest neighbours with the L2 distance.
cv.setRNGSeed(42)
sift = cv.SIFT_create()
kp_ref, des_ref = sift.detectAndCompute(gray_ref, None)
kp_and_des_list = [sift.detectAndCompute(gray, None) for gray in gray_im_list]
if des_ref is None:
    raise ValueError("No SIFT descriptors found in the reference.")
bf = cv.BFMatcher(cv.NORM_L2)
good_matches = []
for name, (keypoints, descriptors) in zip(pcb_names, kp_and_des_list):
    matches = [] if descriptors is None else bf.knnMatch(descriptors, des_ref, k=2)
    good = [pair[0] for pair in matches
            if len(pair) == 2 and pair[0].distance < 0.8 * pair[1].distance]
    good_matches.append(good)
    print(f"{name}: {len(good)} good matches")

# Estimate the mapping from each PCB to the reference using RANSAC.
homography_list = []
inlier_mask_list = []
for name, (kp_im, _), good in zip(pcb_names, kp_and_des_list, good_matches):
    H, mask = None, None
    if len(good) >= 4:
        src_pts = np.float32([kp_im[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_ref[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        H, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
    homography_list.append(H)
    inlier_mask_list.append(mask)
    if H is None or mask is None:
        print(f"{name}: homography unavailable (insufficient or degenerate matches)")
    else:
        print(f"{name}: {int(mask.sum())} RANSAC inliers / {len(good)} good matches")

fig, axes = plt.subplots(2, 3, figsize=(18, 8), constrained_layout=False)
for i, ax in enumerate(axes.flat):
    ax.axis("off")
    if i >= len(im_list):
        continue
    ax.set_title(f"RANSAC Feature Matches — {pcb_names[i]}")
    if homography_list[i] is None:
        ax.text(0.5, 0.5, "Homography estimation failed", ha="center")
        continue
    matched_image = cv.drawMatches(
        im_list[i], kp_and_des_list[i][0], ref, kp_ref, good_matches[i], None,
        matchesMask=inlier_mask_list[i].ravel().tolist(),
        flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
    ax.imshow(cv.cvtColor(matched_image, cv.COLOR_BGR2RGB))
fig.tight_layout()
plt.show()
'''
differences = '''# Align each PCB and compare it with the reference.
aligned_images = []
difference_images = []
binary_difference_images = []
h, w = ref.shape[:2]
for name, im, H in zip(pcb_names, im_list, homography_list):
    if H is None:
        aligned_images.append(None)
        difference_images.append(None)
        binary_difference_images.append(None)
        continue
    aligned = cv.warpPerspective(im, H, (w, h))
    valid_mask = cv.warpPerspective(
        np.full(im.shape[:2], 255, dtype=np.uint8), H, (w, h),
        flags=cv.INTER_NEAREST)
    valid_mask = cv.erode(valid_mask, np.ones((5, 5), np.uint8),
                          borderType=cv.BORDER_CONSTANT, borderValue=0)
    difference = cv.absdiff(ref, aligned)
    difference_gray = cv.cvtColor(difference, cv.COLOR_BGR2GRAY)
    difference_gray[valid_mask == 0] = 0
    _, difference_binary = cv.threshold(difference_gray, 40, 255, cv.THRESH_BINARY)
    aligned_images.append(aligned)
    difference_images.append(difference_gray)
    binary_difference_images.append(difference_binary)
    print(f"{name}: alignment completed")

for i, name in enumerate(pcb_names):
    if aligned_images[i] is None:
        continue
    fig, axes = plt.subplots(1, 4, figsize=(18, 5), constrained_layout=False)
    axes[0].imshow(cv.cvtColor(im_list[i], cv.COLOR_BGR2RGB))
    axes[1].imshow(cv.cvtColor(aligned_images[i], cv.COLOR_BGR2RGB))
    axes[2].imshow(difference_images[i], cmap="gray", vmin=0, vmax=255)
    axes[3].imshow(binary_difference_images[i], cmap="gray", vmin=0, vmax=255)
    for ax, title in zip(axes, ["Original PCB", "Aligned PCB", "Absolute Difference",
                                "Thresholded Difference"]):
        ax.set_title(title)
        ax.axis("off")
    fig.suptitle(name)
    fig.tight_layout()
    plt.show()
'''
path = Path("getting_started.ipynb")
nb = json.loads(path.read_text(encoding="utf-8"))
# Replace a saved Q4 section if present; preserve preceding work.
start = next((i for i, c in enumerate(nb['cells'])
              if c['cell_type'] == 'markdown' and ''.join(c['source']).startswith('## 4.')), len(nb['cells']))
nb['cells'][start:] = [
    {'cell_type': 'markdown', 'metadata': {}, 'source': [
        '## 4. PCB alignment and difference detection\n', '\n',
        'SIFT features are matched with a 0.8 Lowe ratio test. RANSAC estimates '
        'a homography with a 5-pixel threshold. Each PCB is warped into the '
        'reference frame, then absolute differences are thresholded at 40. '
        'An eroded validity mask excludes warped borders. Bright regions may '
        'also reflect lighting or registration errors, so they are candidate differences.\n']},
    *[{'cell_type': 'code', 'metadata': {}, 'execution_count': None,
       'outputs': [], 'source': s.splitlines(keepends=True)} for s in [code, differences]]]
path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
if __name__ == '__main__':
    import matplotlib
    matplotlib.use('Agg')
    namespace = {}
    exec(code, namespace)
    namespace['plt'].show = lambda: namespace['plt'].close('all')
    exec(differences, namespace)
    assert len(namespace['aligned_images']) == 5
    assert all(H is not None for H in namespace['homography_list'])
    print('Verified: all five PCBs matched, aligned, and compared.')
