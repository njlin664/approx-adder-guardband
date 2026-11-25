# slowdown_sweep.py - Day 15(a): does LOA beat TruA at EVERY slowdown, not just x1.08 and x1.37?
# Run with:  python3 src/slowdown_sweep.py          (ripple adders from delay.csv)
#            python3 src/slowdown_sweep.py fast     (fast adders from delay_fast.csv, Day 15(c))
import csv, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FAST = len(sys.argv) > 1 and sys.argv[1] == "fast"
DELAY_CSV = "data/delay_fast.csv" if FAST else "data/delay.csv"
PNG = "figures/slowdown_sweep_fast.png" if FAST else "figures/slowdown_sweep.png"

delay = {(r["design"], int(r["k"])): float(r["delay_ps"]) for r in csv.DictReader(open(DELAY_CSV))}
mse = {(r["design"], int(r["k"])): float(r["MSE"]) for r in csv.DictReader(open("data/results.csv"))}
d0 = delay[("exact", 0)]

FAMILIES = [("trua", "TruA-k (truncation)", "#2a78d6", "o"),
            ("loa",  "LOA-k (lower-part OR)", "#eb6834", "s"),
            ("esa",  "ESA-s (segmentation)", "#1baf7a", "^")]
factors = np.round(np.arange(1.05, 1.501, 0.05), 2)     # 1.00 would need no approximation at all

def best_pick(fam, budget):
    """Among the designs of one family that meet the budget, the one with the lowest MSE."""
    ok = [k for (f, k) in delay if f == fam and delay[(f, k)] <= budget and (f, k) in mse]
    if not ok:
        return None, None
    k = min(ok, key=lambda kk: mse[(fam, kk)])
    return k, mse[(fam, k)]

table = []
for factor in factors:
    budget = d0 / factor
    table.append((factor, budget, {fam: best_pick(fam, budget) for fam, *_ in FAMILIES}))

fig, ax = plt.subplots(figsize=(8, 4.6))
for fam, label, color, marker in FAMILIES:
    xs = [f for f, _, picks in table if picks[fam][1] is not None]
    ys = [picks[fam][1] for _, _, picks in table if picks[fam][1] is not None]
    ax.semilogy(xs, ys, marker=marker, color=color, label=label, drawstyle="steps-post",
                markersize=5, linewidth=1.6)
ax.set_xlabel("slowdown factor (x1.08 = 10 years of aging, x1.37 = 70 C)")
ax.set_ylabel("lowest MSE that still meets timing (log)")
ax.set_title(f"Best error per family at each slowdown ({'fast' if FAST else 'ripple'} adders)",
             loc="left", fontsize=10.5)
for x in (1.08, 1.37):
    ax.axvline(x, color="#5a6472", linestyle="--", linewidth=0.9)
ax.grid(True, which="major", alpha=0.3)
ax.legend(frameon=False, fontsize=9)
plt.tight_layout()
plt.savefig(PNG, dpi=150)
print("saved", PNG)

print(f"\nfresh accurate adder: {d0:.1f} ps ({DELAY_CSV})")
print(f"{'factor':>6}{'budget':>9}   {'TruA pick':>14}   {'LOA pick':>14}   {'TruA/LOA':>8}   winner")
for factor, budget, picks in table:
    (kt, mt), (kl, ml) = picks["trua"], picks["loa"]
    t = f"TruA-{kt} {mt:.3g}" if kt else "none"
    l = f"LOA-{kl} {ml:.3g}" if kl else "none"
    ratio = f"{mt / ml:.1f}x" if kt and kl else "-"
    winner = "LOA" if kt and kl and ml < mt else ("TruA" if kt and kl and mt < ml else "tie/none")
    print(f"{factor:6.2f}{budget:8.1f}ps   {t:>14}   {l:>14}   {ratio:>8}   {winner}")
