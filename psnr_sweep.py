# psnr_sweep.py - Day 17: image quality (PSNR) for every adder design, over all ten images.
# Run with:  python3 psnr_sweep.py       (about a minute; writes psnr.csv and psnr_vs_k.png)
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from blur import load_images, blur, psnr

DESIGNS  = [("trua", k) for k in range(1, 13)]
DESIGNS += [("loa", k) for k in range(1, 13)]
DESIGNS += [("esa", s) for s in range(2, 9)]
DESIGNS += [("etaii", k) for k in range(2, 9)]       # Day 19
CAP = 100.0          # a perfect image has infinite PSNR; count it as 100 dB when averaging

images = load_images()
exact_out = {name: blur(img, "exact") for name, img in images.items()}

rows, mean_psnr = [], {}
for design, k in DESIGNS:
    values = []
    for name, img in images.items():
        p = psnr(exact_out[name], blur(img, design, k))
        values.append(min(p, CAP))
        rows.append([design, k, name, f"{p:.2f}"])
    mean_psnr[(design, k)] = np.mean(values)
    worst = min(values)
    print(f"{design:>5}-{k:<2d}  mean PSNR {mean_psnr[(design, k)]:6.2f} dB   worst image {worst:6.2f} dB")

with open("psnr.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["design", "k", "image", "psnr_db"])
    w.writerows(rows)
print("wrote psnr.csv")

fig, ax = plt.subplots(figsize=(8, 4.6))
for design, label, color, marker in [("trua", "TruA-k", "#2a78d6", "o"),
                                     ("loa", "LOA-k", "#eb6834", "s"),
                                     ("esa", "ESA-s", "#1baf7a", "^"),
                                     ("etaii", "ETAII-k", "#8b5cf6", "D")]:
    ks = sorted(k for d, k in mean_psnr if d == design)
    ax.plot(ks, [mean_psnr[(design, k)] for k in ks], marker=marker, color=color, label=label)
ax.axhline(30, color="#5a6472", linestyle="--", linewidth=1)
ax.text(12.4, 30.8, "30 dB target", color="#5a6472", fontsize=8.5, ha="right")
ax.set_xlabel("k (or segment size s for ESA)")
ax.set_ylabel(f"mean PSNR over 10 images (dB, capped at {CAP:.0f})")
ax.set_title("Blur quality vs. approximation: higher is better", loc="left", fontsize=10.5)
ax.grid(True, alpha=0.3)
ax.legend(frameon=False)
plt.tight_layout()
plt.savefig("psnr_vs_k.png", dpi=150)
print("saved psnr_vs_k.png")
