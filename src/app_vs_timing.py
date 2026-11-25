# app_vs_timing.py - Day 18: do the designs that meet timing (Day 13 picks) still give a good image?
# Run with:  python3 src/app_vs_timing.py     (needs picks.csv, psnr.csv; uses picks_fast.csv if present)
import csv, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from blur import load_images, blur, psnr

NAMES = {"trua": "TruA", "loa": "LOA", "esa": "ESA", "etaii": "ETAII"}
mean_psnr = {}
for r in csv.DictReader(open("data/psnr.csv")):
    mean_psnr.setdefault((r["design"], int(r["k"])), []).append(min(float(r["psnr_db"]), 100.0))
mean_psnr = {key: np.mean(v) for key, v in mean_psnr.items()}

runs = [("ripple adders", "data/picks.csv")]
if os.path.exists("data/picks_fast.csv"):
    runs.append(("fast adders", "data/picks_fast.csv"))

print(f"{'adders':<14}{'scenario':<20}{'pick':<9}{'MSE':>10}{'mean PSNR':>11}   30 dB?")
for label, path in runs:
    for p in csv.DictReader(open(path)):
        key = (p["design"], int(p["k"]))
        q = mean_psnr[key]
        print(f"{label:<14}{p['scenario']:<20}{NAMES[p['design']] + '-' + p['k']:<9}"
              f"{float(p['MSE']):>10.4g}{q:>9.1f} dB   {'yes' if q >= 30 else 'NO'}")

# Side-by-side picture for the 70 C picks (the harder scenario), one row per synthesis mode.
img = load_images()["camera"]
ref = blur(img, "exact")
picks70 = [[p for p in csv.DictReader(open(path)) if "70" in p["scenario"]] for _, path in runs]
ncol = 1 + max(len(p) for p in picks70)
fig, axes = plt.subplots(len(runs), ncol, figsize=(2.5 * ncol, 2.75 * len(runs)), squeeze=False)
for row, (label, path) in enumerate(runs):
    picks = picks70[row]
    for col in range(1 + len(picks), ncol):
        axes[row][col].axis("off")
    panels = [("exact adder", ref)] + [(f"{NAMES[p['design']]}-{p['k']}", blur(img, p["design"], int(p["k"])))
                                       for p in picks]
    for col, (title, out) in enumerate(panels):
        ax = axes[row][col]
        ax.imshow(out, cmap="gray", vmin=0, vmax=255)
        q = psnr(ref, out)
        ax.set_title(title + ("" if col == 0 else f"\n{q:.1f} dB"), fontsize=9)
        ax.set_xticks([]); ax.set_yticks([])
    axes[row][0].set_ylabel(f"70 C, {label}", fontsize=9)
plt.tight_layout(h_pad=1.5)
plt.savefig("figures/app_70C.png", dpi=150)
print("saved figures/app_70C.png")
